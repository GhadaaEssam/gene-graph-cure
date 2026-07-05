import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.gc_pge_service import GC_PGE_Service
from app.services.model_service_registry import ModelServiceRegistry


class UploadedFileStub:
    def __init__(self, content: str) -> None:
        self.content = content.encode("utf-8")

    async def read(self) -> bytes:
        return self.content


class LoadedModelStub:
    def to(self, device):
        return self

    def eval(self):
        return self


class GCPGESingleOmicsFlowTest(unittest.IsolatedAsyncioTestCase):
    async def test_predict_from_files_aligns_geo_before_single_omics_prediction(self):
        with service_for_static_inputs() as service:
            upload = UploadedFileStub("sample_id,B,A,C,EXTRA\ns1,2,1,3,99\n")

            with patch.object(service, "predict", return_value={"ok": True}) as predict:
                result = await service.predict_from_files(
                    {"geo_features": upload},
                    include_graph=False,
                )

            self.assertEqual(result, {"ok": True})
            raw_input = predict.call_args.args[0]
            self.assertFalse(predict.call_args.kwargs["include_graph"])
            self.assertEqual(list(raw_input["geo_features"].columns), ["A", "B", "C", "D"])
            self.assertEqual(raw_input["geo_features"].to_dict("records"), [
                {"A": 1, "B": 2, "C": 3, "D": 40},
            ])
            self.assertEqual(raw_input["_input_alignment"]["missing_gene_names"], ["D"])
            self.assertEqual(raw_input["_input_alignment"]["fill_strategy"], "training_median")
            self.assertEqual(raw_input["_node_names"], ["A", "B", "C", "D"])
            self.assertEqual(raw_input["_pathway_names"], ["p0", "p1"])
            self.assertEqual(raw_input["_anchor_indices"], {0, 2})

    async def test_predict_from_files_rejects_missing_geo_upload(self):
        with service_for_static_inputs() as service:
            with self.assertRaisesRegex(ValueError, "geo_features file is required"):
                await service.predict_from_files({})

    def test_filter_heavy_outputs_replaces_graph_with_shape(self):
        with service_for_static_inputs() as service:
            filtered = service._filter_heavy_outputs(
                {"out": [1], "graph": [[0.1, 0.2], [0.3, 0.4]]},
                include_graph=False,
            )

            self.assertNotIn("graph", filtered)
            self.assertEqual(filtered["graph_shape"], [2, 2])

    def test_filter_heavy_outputs_keeps_graph_with_shape_when_included(self):
        with service_for_static_inputs() as service:
            filtered = service._filter_heavy_outputs(
                {"out": [1], "graph": [[0.1, 0.2], [0.3, 0.4]]},
                include_graph=True,
            )

            self.assertEqual(filtered["graph"], [[0.1, 0.2], [0.3, 0.4]])
            self.assertEqual(filtered["graph_shape"], [2, 2])


class ModelServiceRegistryTest(unittest.TestCase):
    def test_registry_normalizes_keys_caches_service_and_uses_static_input_dir(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            weights_dir = root / "weights"
            inputs_dir = root / "model_inputs"
            liver_inputs = inputs_dir / "liver"
            weights_dir.mkdir()
            liver_inputs.mkdir(parents=True)
            (weights_dir / "liver_model.pt").touch()

            registry = ModelServiceRegistry(
                weights_dir=weights_dir,
                model_inputs_dir=inputs_dir,
                model_files={"liver": "liver_model.pt"},
            )

            with patch(
                "app.services.model_service_registry.GC_PGE_Service",
                return_value="service",
            ) as service_factory:
                first = registry.get_service(" Liver ")
                second = registry.get_service("liver")

            self.assertEqual(first, "service")
            self.assertIs(first, second)
            service_factory.assert_called_once_with(
                model_path=str(weights_dir / "liver_model.pt"),
                static_inputs_dir=liver_inputs,
            )

    def test_registry_rejects_unknown_model_key(self):
        registry = ModelServiceRegistry(
            weights_dir=Path("weights"),
            model_inputs_dir=Path("model_inputs"),
            model_files={"breast": "breast_model.pt"},
        )

        with self.assertRaisesRegex(ValueError, "Unsupported model 'unknown'"):
            registry.get_service("unknown")


class service_for_static_inputs:
    def __init__(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def __enter__(self) -> GC_PGE_Service:
        directory = Path(self.temp_dir.name)
        self.static_inputs_dir = directory / "model_inputs"
        self.static_inputs_dir.mkdir()
        self.model_path = directory / "model.pt"
        self.model_path.touch()

        pd.DataFrame({"gene": ["A", "B", "C", "D"]}).to_csv(
            self.static_inputs_dir / "expected_geo_genes.csv",
            index=False,
        )
        pd.DataFrame({"gene": ["A", "B", "C", "D"], "median": [10, 20, 30, 40]}).to_csv(
            self.static_inputs_dir / "geo_gene_medians.csv",
            index=False,
        )
        pd.DataFrame({"gene": ["A", "B", "C", "D"], "result_num": [1, 0, 1, 0]}).to_csv(
            self.static_inputs_dir / "anchor_genes.csv",
            index=False,
        )
        pd.DataFrame(
            {
                "gene": ["A", "B", "C", "D"],
                "p0": [0.1, 0.2, 0.3, 0.4],
                "p1": [0.5, 0.6, 0.7, 0.8],
            }
        ).to_csv(self.static_inputs_dir / "node_features.csv", index=False)
        pd.DataFrame({"source": [0, 1], "target": [1, 2]}).to_csv(
            self.static_inputs_dir / "ppi_edges.csv",
            index=False,
        )
        pd.DataFrame({"source": [0], "target": [2]}).to_csv(
            self.static_inputs_dir / "homolog_edges.csv",
            index=False,
        )

        self.load_model_patch = patch.object(
            GC_PGE_Service,
            "_load_model",
            return_value=LoadedModelStub(),
        )
        self.pathway_labels_patch = patch.object(
            GC_PGE_Service,
            "_load_pathway_id_labels",
            return_value=[],
        )
        self.load_model_patch.start()
        self.pathway_labels_patch.start()
        return GC_PGE_Service(
            model_path=str(self.model_path),
            static_inputs_dir=self.static_inputs_dir,
        )

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.pathway_labels_patch.stop()
        self.load_model_patch.stop()
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
