from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Hashable, Literal

import pandas as pd


Orientation = Literal["genes_as_columns", "genes_as_rows"]


@dataclass(frozen=True)
class GeneIndex:
    orientation: Orientation
    gene_names: list[str]
    expression: pd.DataFrame
    gene_axis_name: Hashable | None = None


class GeneExpressionAligner:
    """
    Align uploaded GEO expression data to the immutable model gene contract.

    Output is always samples x expected genes, with expected genes in contract
    order. Missing genes are filled from the per-gene training medians.
    """

    def __init__(
        self,
        expected_genes_path: str | Path,
        medians_path: str | Path,
        min_match_rate: float = 0.7,
    ) -> None:
        self.expected_genes_path = Path(expected_genes_path)
        self.medians_path = Path(medians_path)
        self.min_match_rate = min_match_rate

        self.expected_genes = self._load_expected_genes(self.expected_genes_path)
        self.normalized_expected = {
            self._normalize_name(gene): gene for gene in self.expected_genes
        }
        self.medians = self._load_medians(self.medians_path)
        missing_medians = [
            gene for gene in self.expected_genes if gene not in self.medians
        ]
        if missing_medians:
            examples = ", ".join(missing_medians[:10])
            raise ValueError(
                f"{self.medians_path} is missing medians for "
                f"{len(missing_medians)} expected genes. Examples: {examples}"
            )

    def align(self, data_sample: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        orientation = self._detect_orientation(data_sample)
        gene_index = self._extract_gene_index(data_sample, orientation)
        normalized_names, duplicate_upload_genes = self._normalize_names(
            gene_index.gene_names
        )
        match_report = self._match_genes(normalized_names, duplicate_upload_genes)

        deduplicated = self._deduplicate_expression_columns(
            gene_index.expression,
            normalized_names,
        )
        aligned_df = self._build_aligned_frame(deduplicated)
        alignment_report = {
            **match_report,
            "orientation": gene_index.orientation,
            "gene_axis_name": gene_index.gene_axis_name,
            "fill_strategy": "training_median",
            "min_match_rate": self.min_match_rate,
        }

        self._validate(alignment_report)
        return aligned_df, alignment_report

    def _detect_orientation(self, data_sample: pd.DataFrame) -> Orientation:
        column_score = self._count_expected_matches(data_sample.columns)
        row_score = max(
            (
                self._count_expected_matches(data_sample[column])
                for column in data_sample.columns
            ),
            default=0,
        )

        if row_score > column_score:
            return "genes_as_rows"
        return "genes_as_columns"

    def _extract_gene_index(
        self,
        data_sample: pd.DataFrame,
        orientation: Orientation,
    ) -> GeneIndex:
        if orientation == "genes_as_rows":
            gene_column = self._find_gene_name_column(data_sample)
            expression = data_sample.drop(columns=[gene_column])
            expression = self._drop_empty_or_index_columns(expression)
            expression = expression.apply(pd.to_numeric, errors="coerce").T
            expression.columns = data_sample[gene_column].astype(str).tolist()
            return GeneIndex(
                orientation=orientation,
                gene_names=list(expression.columns),
                expression=expression,
                gene_axis_name=str(gene_column),
            )

        expression = self._drop_empty_or_index_columns(data_sample)
        expression = self._drop_sample_identifier_column(expression)
        expression = expression.apply(pd.to_numeric, errors="coerce")
        return GeneIndex(
            orientation=orientation,
            gene_names=[str(column) for column in expression.columns],
            expression=expression,
            gene_axis_name="header",
        )

    def _normalize_names(
        self,
        names: list[str],
    ) -> tuple[list[str], dict[str, int]]:
        normalized_names = [self._normalize_name(name) for name in names]
        counts: dict[str, int] = {}
        for name in normalized_names:
            counts[name] = counts.get(name, 0) + 1

        duplicate_upload_genes = {
            self.normalized_expected.get(name, name): count
            for name, count in counts.items()
            if name and count > 1
        }
        return normalized_names, duplicate_upload_genes

    def _match_genes(
        self,
        normalized_names: list[str],
        duplicate_upload_genes: dict[str, int],
    ) -> dict:
        uploaded_expected_genes = {
            self.normalized_expected[name]
            for name in normalized_names
            if name in self.normalized_expected
        }
        matched_genes = [
            gene for gene in self.expected_genes if gene in uploaded_expected_genes
        ]
        missing_genes = [
            gene for gene in self.expected_genes if gene not in uploaded_expected_genes
        ]
        extra_genes = sorted(
            {
                name
                for name in normalized_names
                if name and name not in self.normalized_expected
            }
        )

        expected_count = len(self.expected_genes)
        matched_count = len(matched_genes)
        return {
            "expected_genes": expected_count,
            "uploaded_genes": len([name for name in normalized_names if name]),
            "matched_genes": matched_count,
            "missing_genes": len(missing_genes),
            "extra_genes": len(extra_genes),
            "duplicate_genes": duplicate_upload_genes,
            "match_rate": matched_count / expected_count if expected_count else 0.0,
        }

    def _validate(self, alignment_report: dict) -> None:
        if alignment_report["match_rate"] < self.min_match_rate:
            raise ValueError(
                "Uploaded GEO genes match only "
                f"{alignment_report['match_rate']:.1%} of the expected model "
                f"contract; minimum is {self.min_match_rate:.1%}."
            )

    def _deduplicate_expression_columns(
        self,
        expression: pd.DataFrame,
        normalized_names: list[str],
    ) -> pd.DataFrame:
        normalized_columns = [
            self.normalized_expected.get(name, name) for name in normalized_names
        ]
        expression = expression.copy()
        expression.columns = normalized_columns
        return expression.T.groupby(level=0, sort=False).median().T

    def _build_aligned_frame(self, expression: pd.DataFrame) -> pd.DataFrame:
        aligned = pd.DataFrame(
            {
                gene: (
                    expression[gene]
                    if gene in expression.columns
                    else self.medians[gene]
                )
                for gene in self.expected_genes
            },
            index=expression.index,
        )
        return aligned.reset_index(drop=True)

    def _find_gene_name_column(self, data_sample: pd.DataFrame) -> Hashable:
        scored_columns = [
            (self._count_expected_matches(data_sample[column]), column)
            for column in data_sample.columns
        ]
        scored_columns.sort(key=lambda item: item[0], reverse=True)
        if not scored_columns or scored_columns[0][0] == 0:
            raise ValueError("Could not find a gene-name column in uploaded GEO data.")
        return scored_columns[0][1]

    def _drop_empty_or_index_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        columns_to_drop = [
            column
            for column in data.columns
            if self._is_empty_or_index_column(column)
        ]
        return data.drop(columns=columns_to_drop)

    def _drop_sample_identifier_column(self, data: pd.DataFrame) -> pd.DataFrame:
        if data.empty:
            return data

        first_column = data.columns[0]
        first_column_name = self._normalize_name(first_column)
        if first_column_name in self.normalized_expected:
            return data
        if first_column_name in {"ID", "SAMPLE", "SAMPLE_ID", "PATIENT", "PATIENT_ID"}:
            return data.drop(columns=[first_column])

        first_values = data[first_column].astype(str)
        numeric_ratio = pd.to_numeric(first_values, errors="coerce").notna().mean()
        if numeric_ratio < 0.5:
            return data.drop(columns=[first_column])
        return data

    def _count_expected_matches(self, names) -> int:
        return sum(
            1
            for name in names
            if self._normalize_name(name) in self.normalized_expected
        )

    @staticmethod
    def _normalize_name(name) -> str:
        return str(name).strip().upper()

    @staticmethod
    def _is_empty_or_index_column(column) -> bool:
        column_name = str(column).strip()
        return not column_name or column_name.startswith("Unnamed:")

    @staticmethod
    def _load_expected_genes(path: Path) -> list[str]:
        expected = pd.read_csv(path)
        if list(expected.columns) != ["gene"]:
            raise ValueError(f"{path} must contain exactly one column named 'gene'")
        return expected["gene"].astype(str).str.strip().tolist()

    @staticmethod
    def _load_medians(path: Path) -> dict[str, float]:
        medians = pd.read_csv(path)
        if not {"gene", "median"}.issubset(medians.columns):
            raise ValueError(f"{path} must contain 'gene' and 'median' columns")
        return dict(
            zip(
                medians["gene"].astype(str).str.strip(),
                medians["median"].astype(float),
            )
        )