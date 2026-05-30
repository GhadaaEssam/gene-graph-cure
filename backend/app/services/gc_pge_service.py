import io
import logging
import sys
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd
import torch


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gcpge"))

import model

sys.modules["model.model"] = model

from app.services.gene_expression_aligner import (
    GeneExpressionAligner,
    MultiOmicsGeneExpressionAligner,
)
from gcpge.preprocess import preprocess_for_inference


logger = logging.getLogger(__name__)


class GC_PGE_Service:
    CORE_RESULT_LIMIT = 10
    ALIGNMENT_EXAMPLE_LIMIT = 5
    MULTIOMICS_FILE_KEYS = ("meth_features", "cnv_features", "snv_features")
    STATIC_INPUT_FILENAMES = {
        "anchor_genes": ("anchor_genes.csv",),
        "node_features": ("node_features.csv",),
        "ppi_edges": ("ppi_edges.csv",),
        "homolog_edges": ("homolog_edges.csv", "homolg_edges.csv"),
        "expected_geo_genes": ("expected_geo_genes.csv",),
        "geo_gene_medians": ("geo_gene_medians.csv", "rna_gene_medians.csv"),
    }
    EPSILON = np.finfo(float).eps

    def __init__(
        self,
        model_path: str,
        static_inputs_dir: Path,
        multiomics_model_paths: list[str] | None = None,
    ):
        model_path_obj = Path(model_path)
        if not model_path_obj.exists():
            raise FileNotFoundError(f"Model weights not found at: {model_path}")

        self.static_inputs_dir = Path(static_inputs_dir)
        self._validate_static_inputs(self.static_inputs_dir)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pathway_id_labels = self._load_pathway_id_labels(
            PROJECT_ROOT / "gcpge" / "pw_id.csv"
        )
        self.gene_identifier_aliases = self._load_gene_identifier_aliases()
        self.gene_aligner = GeneExpressionAligner(
            expected_genes_path=self._static_input_path("expected_geo_genes"),
            medians_path=self._static_input_path("geo_gene_medians"),
            gene_aliases=self.gene_identifier_aliases,
        )
        self.multiomics_aligner = self._build_multiomics_aligner()

        self.model = self._load_model(str(model_path_obj))
        self.multiomics_models = [
            self._load_model(path)
            for path in (multiomics_model_paths or [])
            if path
        ]
        if not self.multiomics_models and self._supports_multiomics(self.model):
            self.multiomics_models = [self.model]

    async def predict_from_files(
        self,
        files_dict: Mapping[str, object],
        include_graph: bool = True,
    ):
        contents: dict[str, bytes] = {}

        for key, uploaded_file in files_dict.items():

            if key == "cancer_type":
                continue

            if uploaded_file is None:
                continue

            if hasattr(uploaded_file, "read"):
                contents[key] = await uploaded_file.read()
            else:
                raise ValueError(f"Invalid file type for {key}: expected UploadFile")
            
        if "geo_features" not in contents:
            raise ValueError("geo_features file is required")

        has_multiomics = any(key in contents for key in self.MULTIOMICS_FILE_KEYS)
        has_all_multiomics = all(key in contents for key in self.MULTIOMICS_FILE_KEYS)
        if has_multiomics and not has_all_multiomics:
            missing = [key for key in self.MULTIOMICS_FILE_KEYS if key not in contents]
            raise ValueError(
                "Multi-omics prediction requires all optional files: "
                f"{', '.join(missing)}"
            )

        processed_data = self._build_base_input(contents)
        if has_all_multiomics:
            if self.multiomics_aligner is None:
                raise ValueError(
                    "This model input folder is not configured for multi-omics alignment"
                )
            processed_data["omics"] = self._build_multiomics_input(contents)

        return self.predict(processed_data, include_graph=include_graph)

    def predict(self, raw_input: dict, include_graph: bool = True):
        if "omics" in raw_input:
            return self.predict_multiomics(raw_input, include_graph=include_graph)
        return self.predict_base(raw_input, include_graph=include_graph)

    def predict_base(self, raw_input: dict, include_graph: bool = True):
        with torch.no_grad():
            data, geo_tensor = preprocess_for_inference(raw_input)
            data = data.to(self.device)
            geo_tensor = geo_tensor.to(self.device)

            result = self.model(data, geo_tensor)
            json_result = self._to_json_serializable(result, collapse_out=True)
            self._add_common_metadata(json_result, raw_input)
            return self._filter_heavy_outputs(json_result, include_graph=include_graph)

    def predict_multiomics(self, raw_input: dict, include_graph: bool = True):
        if not self.multiomics_models:
            raise ValueError(
                "Multi-omics files were provided, but no multi-omics checkpoint is configured"
            )

        with torch.no_grad():
            data, _ = preprocess_for_inference(raw_input)
            data = data.to(self.device)

            omics = raw_input["omics"]
            x_rna = self._frame_to_tensor(omics["data_geo_x"])
            x_meth = self._frame_to_tensor(omics["data_meth_x"])
            x_cnv = self._frame_to_tensor(omics["data_cnv_x"])
            x_snv = self._frame_to_tensor(omics["data_snv_x"])

            accumulated: dict[str, torch.Tensor] = {}
            log_probability_keys = {"out", "out_multiomics", "temp"}

            for loaded_model in self.multiomics_models:
                if not self._supports_multiomics(loaded_model):
                    raise ValueError(
                        "Configured checkpoint does not include the multi-omics branch"
                    )

                result = loaded_model(
                    data,
                    x_rna,
                    x_meth=x_meth,
                    x_cnv=x_cnv,
                    x_snv=x_snv,
                )
                if "out_multiomics" not in result:
                    raise RuntimeError("Multi-omics model did not return 'out_multiomics'")

                for key, value in result.items():
                    if not isinstance(value, torch.Tensor):
                        continue
                    value_to_add = torch.exp(value) if key in log_probability_keys else value
                    accumulated[key] = accumulated.get(key, 0) + value_to_add

            averaged = {}
            for key, value in accumulated.items():
                averaged_value = value / len(self.multiomics_models)
                if key in log_probability_keys:
                    averaged_value = torch.log(averaged_value.clamp_min(self.EPSILON))
                averaged[key] = averaged_value

            probabilities = torch.exp(averaged["out_multiomics"])
            averaged["out_multiomics_probabilities"] = probabilities
            averaged["prediction"] = probabilities.argmax(dim=1)
            averaged["sample_ids"] = omics["sample_ids"]
            averaged["gene_ids"] = omics["gene_ids"]
            averaged["multiomics_alignment"] = self._summarize_alignment_report(
                omics["alignment_report"]
            )

            json_result = self._to_json_serializable(averaged, collapse_out=True)
            self._add_common_metadata(json_result, raw_input)
            return self._filter_heavy_outputs(json_result, include_graph=include_graph)

    def _build_base_input(self, contents: Mapping[str, bytes]) -> dict:
        data_sample = pd.read_csv(io.BytesIO(contents["geo_features"]), header=0)
        logger.info(
            "Uploaded GEO table summary: shape=%s columns_sample=%s",
            data_sample.shape,
            [str(column) for column in data_sample.columns[:5]],
        )

        aligned_geo, alignment_report = self.gene_aligner.align(data_sample)
        logger.info(
            "GEO alignment summary: %s",
            self._summarize_alignment_report(alignment_report),
        )

        anchor_genes = pd.read_csv(self._static_input_path("anchor_genes"), header=0)
        data_x_raw = pd.read_csv(self._static_input_path("node_features"), header=0)

        processed_data = {
            "geo_features": aligned_geo,
            "_input_alignment": alignment_report,
            "anchor_genes": anchor_genes,
            "_anchor_gene_names": self._extract_gene_names(anchor_genes),
            "node_features": data_x_raw.iloc[:, 1:],
            "ppi_edges": pd.read_csv(self._static_input_path("ppi_edges"), header=0),
            "homolog_edges": pd.read_csv(
                self._static_input_path("homolog_edges"),
                header=0,
            ),
        }
        processed_data["_node_names"] = self._merge_preferred_labels(
            processed_data["_anchor_gene_names"],
            data_x_raw.iloc[:, 0].astype(str).tolist(),
        )
        processed_data["_pathway_names"] = self._resolve_pathway_names(
            [str(column) for column in data_x_raw.columns[1:]]
        )
        if "result_num" in anchor_genes.columns:
            processed_data["_anchor_indices"] = set(
                int(index)
                for index in anchor_genes.index[anchor_genes["result_num"] == 1]
            )
        else:
            processed_data["_anchor_indices"] = set()

        return processed_data

    def _build_multiomics_input(self, contents: Mapping[str, bytes]) -> dict:
        assert self.multiomics_aligner is not None
        aligned, alignment_report = self.multiomics_aligner.align(
            {
                "rna": pd.read_csv(io.BytesIO(contents["geo_features"]), header=0),
                "meth": pd.read_csv(io.BytesIO(contents["meth_features"]), header=0),
                "cnv": pd.read_csv(io.BytesIO(contents["cnv_features"]), header=0),
                "snv": pd.read_csv(io.BytesIO(contents["snv_features"]), header=0),
            }
        )
        logger.info(
            "Multi-omics alignment summary: %s",
            self._summarize_alignment_report(alignment_report),
        )

        return {
            "data_geo_x": aligned["rna"],
            "data_meth_x": aligned["meth"],
            "data_cnv_x": aligned["cnv"],
            "data_snv_x": aligned["snv"],
            "sample_ids": [str(index) for index in aligned["rna"].index.tolist()],
            "gene_ids": aligned["rna"].columns.astype(str).tolist(),
            "alignment_report": alignment_report,
        }

    def _load_model(self, model_path: str):
        loaded_model = torch.load(
            model_path,
            map_location=self.device,
            weights_only=False,
        )
        loaded_model.to(self.device)
        loaded_model.eval()
        return loaded_model

    @staticmethod
    def _supports_multiomics(loaded_model) -> bool:
        return all(
            hasattr(loaded_model, attr)
            for attr in ("enc_meth", "enc_cnv", "enc_snv", "fusion", "final_classifier")
        )

    def _frame_to_tensor(self, frame: pd.DataFrame) -> torch.Tensor:
        return torch.tensor(frame.values, dtype=torch.float).to(self.device)

    @classmethod
    def _validate_static_inputs(cls, static_inputs_dir: Path) -> None:
        missing_files = []
        for input_name, filenames in cls.STATIC_INPUT_FILENAMES.items():
            if not any((static_inputs_dir / filename).is_file() for filename in filenames):
                missing_files.append(f"{input_name} ({' or '.join(filenames)})")

        if missing_files:
            raise FileNotFoundError(
                f"Missing static model input files in {static_inputs_dir}: "
                f"{', '.join(missing_files)}"
            )

    def _static_input_path(self, input_name: str) -> Path:
        for filename in self.STATIC_INPUT_FILENAMES[input_name]:
            path = self.static_inputs_dir / filename
            if path.is_file():
                return path
        raise FileNotFoundError(
            f"Missing static model input '{input_name}' in {self.static_inputs_dir}"
        )

    def _build_multiomics_aligner(self) -> MultiOmicsGeneExpressionAligner | None:
        expected_path = self.static_inputs_dir / "expected_geo_genes.csv"
        medians_paths = {
            modality: self.static_inputs_dir / filename
            for modality, filename in (
                MultiOmicsGeneExpressionAligner.MODALITY_MEDIAN_FILENAMES.items()
            )
        }
        if not expected_path.exists() or not all(path.exists() for path in medians_paths.values()):
            return None

        return MultiOmicsGeneExpressionAligner(
            expected_genes_path=expected_path,
            medians_paths=medians_paths,
            gene_aliases=self.gene_identifier_aliases,
        )

    def _load_gene_identifier_aliases(self) -> dict[str, str]:
        anchor_path = self._static_input_path("anchor_genes")
        anchor_genes = pd.read_csv(anchor_path, header=0)
        if not {"id", "gene"}.issubset(anchor_genes.columns):
            logger.info(
                "No alternate gene identifier aliases found in %s",
                anchor_path.name,
            )
            return {}

        aliases: dict[str, str] = {}
        for _, row in anchor_genes.iterrows():
            identifier = self._clean_gene_identifier(row.get("id"))
            gene = self._clean_gene_identifier(row.get("gene"))
            if identifier and gene and identifier != gene:
                aliases[identifier] = gene

        logger.info(
            "Loaded gene identifier aliases: count=%d source=%s sample=%s",
            len(aliases),
            anchor_path.name,
            list(aliases.items())[: self.ALIGNMENT_EXAMPLE_LIMIT],
        )
        return aliases

    def _to_json_serializable(self, result: dict, collapse_out: bool = False) -> dict:
        json_result = {}
        for key, value in result.items():
            # if isinstance(value, torch.Tensor):
            #     if collapse_out and key == "out":
            #         value = value.max(dim=1).indices
            #     json_result[key] = value.detach().cpu().tolist()
            # elif isinstance(value, (np.ndarray, np.generic)):
            #     json_result[key] = value.tolist()
            # else:
            #     json_result[key] = value
            if isinstance(value, torch.Tensor):
                if collapse_out and key == "out":
                    probabilities = torch.exp(value)
                    json_result["out_probabilities"] = probabilities.detach().cpu().tolist()
                    value = value.max(dim=1).indices

                json_result[key] = value.detach().cpu().tolist()
        return json_result

    def _filter_heavy_outputs(self, result: dict, include_graph: bool) -> dict:
        if include_graph or "graph" not in result:
            return result

        graph = result.pop("graph")
        if isinstance(graph, list):
            rows = len(graph)
            cols = len(graph[0]) if rows and isinstance(graph[0], list) else 0
            result["graph_shape"] = [rows, cols]
        else:
            result["graph_shape"] = None

        return result

    def _add_common_metadata(self, result: dict, raw_input: dict) -> None:
        self._add_structured_core_results(result, raw_input)
        if "_input_alignment" in raw_input:
            result["input_alignment"] = self._summarize_alignment_report(
                raw_input["_input_alignment"]
            )

    @classmethod
    def _summarize_alignment_report(cls, report: dict) -> dict:
        if not isinstance(report, dict):
            return {}

        if "reports" in report:
            return {
                "modalities": report.get("modalities", []),
                "sample_counts": report.get("sample_counts", {}),
                "reports": {
                    modality: cls._summarize_alignment_report(modality_report)
                    for modality, modality_report in report.get("reports", {}).items()
                },
            }

        summary = {
            key: report.get(key)
            for key in (
                "orientation",
                "gene_axis_name",
                "expected_genes",
                "uploaded_genes",
                "matched_genes",
                "missing_genes",
                "extra_genes",
                "sample_count",
                "match_rate",
                "fill_strategy",
                "min_match_rate",
                "identifier_aliases",
            )
            if key in report
        }

        for key in ("matched_gene_names", "missing_gene_names", "extra_gene_names"):
            names = report.get(key)
            if isinstance(names, list):
                summary[f"{key}_count"] = len(names)
                summary[f"{key}_sample"] = names[:cls.ALIGNMENT_EXAMPLE_LIMIT]

        duplicate_genes = report.get("duplicate_genes")
        if isinstance(duplicate_genes, dict):
            summary["duplicate_gene_count"] = len(duplicate_genes)
            summary["duplicate_gene_sample"] = dict(
                list(duplicate_genes.items())[:cls.ALIGNMENT_EXAMPLE_LIMIT]
            )

        return summary

    def _add_structured_core_results(self, result: dict, raw_input: dict) -> None:
        node_names = raw_input.get("_node_names", [])
        pathway_names = raw_input.get("_pathway_names", [])
        anchor_indices = raw_input.get("_anchor_indices", set())

        gene_scores = self._flatten_numeric_values(result.get("vimp_g"))
        gene_correlations = self._flatten_numeric_values(result.get("cor"))
        structured_core_genes = []
        for index in self._top_indices(gene_scores):
            structured_core_genes.append({
                "index": index,
                "name": self._label_at(node_names, index, f"gene_{index}"),
                "score": float(gene_scores[index]),
                "correlation": (
                    float(gene_correlations[index])
                    if index < len(gene_correlations)
                    else None
                ),
                "is_anchor": index in anchor_indices,
            })

        pathway_weights = self._flatten_numeric_values(result.get("pw_w"))
        structured_core_pathways = []
        for index in self._top_indices(pathway_weights):
            structured_core_pathways.append({
                "index": index,
                "name": self._label_at(pathway_names, index, f"pathway_{index}"),
                "weight": float(pathway_weights[index]),
            })

        result["structured_core_genes"] = structured_core_genes
        result["structured_core_pathways"] = structured_core_pathways
        result["core_genes"] = [gene["name"] for gene in structured_core_genes]
        result["core_pathways"] = [
            pathway["name"] for pathway in structured_core_pathways
        ]

    @classmethod
    def _top_indices(cls, values: list[float]) -> list[int]:
        if not values:
            return []
        return sorted(
            range(len(values)),
            key=lambda index: values[index],
            reverse=True,
        )[:cls.CORE_RESULT_LIMIT]

    @staticmethod
    def _flatten_numeric_values(value) -> list[float]:
        if value is None:
            return []
        return np.asarray(value, dtype=float).reshape(-1).tolist()

    @staticmethod
    def _label_at(labels: list[str], index: int, fallback: str) -> str:
        if index < len(labels) and labels[index]:
            return labels[index]
        return fallback

    @classmethod
    def _extract_gene_names(cls, anchor_genes: pd.DataFrame) -> list[str]:
        if anchor_genes.empty:
            return []

        preferred_columns = {
            "gene",
            "genes",
            "gene_name",
            "genename",
            "gene_symbol",
            "genesymbol",
            "symbol",
            "name",
        }
        candidate_columns = sorted(
            anchor_genes.columns,
            key=lambda column: (
                cls._normalized_column_name(column) not in preferred_columns,
                list(anchor_genes.columns).index(column),
            ),
        )

        for column in candidate_columns:
            normalized_column = cls._normalized_column_name(column)
            if normalized_column == "result_num":
                continue

            values = anchor_genes[column].fillna("").astype(str).str.strip()
            if not cls._looks_like_numeric_ids(values):
                return values.tolist()

        return []

    @staticmethod
    def _merge_preferred_labels(
        preferred_labels: list[str],
        fallback_labels: list[str],
    ) -> list[str]:
        label_count = max(len(preferred_labels), len(fallback_labels))
        labels = []
        for index in range(label_count):
            preferred = preferred_labels[index] if index < len(preferred_labels) else ""
            fallback = fallback_labels[index] if index < len(fallback_labels) else ""
            labels.append(preferred or fallback)
        return labels

    @staticmethod
    def _normalized_column_name(column: str) -> str:
        return str(column).strip().lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _looks_like_numeric_ids(values: pd.Series) -> bool:
        non_empty_values = values[values != ""]
        if non_empty_values.empty:
            return True
        numeric_ratio = pd.to_numeric(non_empty_values, errors="coerce").notna().mean()
        return numeric_ratio >= 0.95

    @staticmethod
    def _load_pathway_id_labels(path: Path) -> list[str]:
        if not path.exists():
            return []

        pathway_ids = pd.read_csv(path)
        if not {"id", "pwid"}.issubset(pathway_ids.columns):
            return []

        labels = [""] * (int(pathway_ids["id"].max()) + 1)
        for _, row in pathway_ids.iterrows():
            labels[int(row["id"])] = str(row["pwid"])
        return labels

    @staticmethod
    def _clean_gene_identifier(value) -> str:
        if pd.isna(value):
            return ""
        return str(value).strip()

    def _resolve_pathway_names(self, uploaded_names: list[str]) -> list[str]:
        if len(self.pathway_id_labels) >= len(uploaded_names):
            return self.pathway_id_labels[:len(uploaded_names)]
        return uploaded_names
