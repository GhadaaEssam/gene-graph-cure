import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.gene_expression_aligner import (
    GeneExpressionAligner,
    MultiOmicsGeneExpressionAligner,
)


class GeneExpressionAlignerTest(unittest.TestCase):
    def test_aligns_genes_as_columns_in_contract_order_and_fills_missing(self):
        with aligner_for(["A", "B", "C"], {"A": 10, "B": 20, "C": 30}) as aligner:
            uploaded = pd.DataFrame(
                {
                    "sample_id": ["s1", "s2"],
                    "B": [2, 5],
                    "A": [1, 4],
                    "EXTRA": [99, 100],
                }
            )

            aligned, report = aligner.align(uploaded)

            self.assertEqual(list(aligned.columns), ["A", "B", "C"])
            self.assertEqual(aligned.to_dict("records"), [
                {"A": 1, "B": 2, "C": 30},
                {"A": 4, "B": 5, "C": 30},
            ])
            self.assertEqual(report["orientation"], "genes_as_columns")
            self.assertEqual(report["matched_genes"], 2)
            self.assertEqual(report["missing_gene_names"], ["C"])
            self.assertEqual(report["extra_gene_names"], ["EXTRA"])
            self.assertEqual(report["contract_match_rate"], 2 / 3)
            self.assertEqual(report["match_rate"], 2 / 4)

    def test_aligns_genes_as_rows_and_normalizes_gene_names(self):
        with aligner_for(["A", "B", "C"], {"A": 10, "B": 20, "C": 30}) as aligner:
            uploaded = pd.DataFrame(
                {
                    "gene": [" a ", "b", "unknown"],
                    "sample_1": [1, 2, 99],
                    "sample_2": [4, 5, 100],
                }
            )

            aligned, report = aligner.align(uploaded)

            self.assertEqual(list(aligned.columns), ["A", "B", "C"])
            self.assertEqual(aligned.to_dict("records"), [
                {"A": 1, "B": 2, "C": 30},
                {"A": 4, "B": 5, "C": 30},
            ])
            self.assertEqual(report["orientation"], "genes_as_rows")
            self.assertEqual(report["gene_axis_name"], "gene")
            self.assertEqual(report["matched_gene_names"], ["A", "B"])

    def test_duplicate_uploaded_genes_are_collapsed_by_sample_median(self):
        with aligner_for(["A", "B", "C"], {"A": 10, "B": 20, "C": 30}) as aligner:
            uploaded = pd.DataFrame(
                [["s1", 1, 3, 7], ["s2", 10, 14, 8]],
                columns=["sample_id", "A", " a ", "B"],
            )

            aligned, report = aligner.align(uploaded)

            self.assertEqual(aligned.to_dict("records"), [
                {"A": 2.0, "B": 7.0, "C": 30.0},
                {"A": 12.0, "B": 8.0, "C": 30.0},
            ])
            self.assertEqual(report["duplicate_genes"], {"A": 2})

    def test_validation_rejects_upload_below_match_threshold(self):
        with aligner_for(
            ["A", "B", "C", "D"],
            {"A": 10, "B": 20, "C": 30, "D": 40},
            min_match_rate=0.75,
        ) as aligner:
            uploaded = pd.DataFrame({"A": [1], "B": [2], "EXTRA": [99]})

            with self.assertRaisesRegex(ValueError, "minimum is 75.0%"):
                aligner.align(uploaded)

    def test_init_rejects_medians_missing_expected_gene(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            expected_path = directory_path / "expected_geo_genes.csv"
            medians_path = directory_path / "geo_gene_medians.csv"
            pd.DataFrame({"gene": ["A", "B"]}).to_csv(expected_path, index=False)
            pd.DataFrame({"gene": ["A"], "median": [10]}).to_csv(
                medians_path,
                index=False,
            )

            with self.assertRaisesRegex(ValueError, "missing medians"):
                GeneExpressionAligner(expected_path, medians_path)


class MultiOmicsGeneExpressionAlignerTest(unittest.TestCase):
    def test_aligns_each_modality_with_its_own_medians(self):
        with multiomics_aligner_for(
            ["A", "B", "C"],
            {
                "rna": {"A": 10, "B": 20, "C": 30},
                "cnv": {"A": 100, "B": 200, "C": 300},
                "snv": {"A": 0, "B": 0, "C": 1},
                "meth": {"A": 0.1, "B": 0.2, "C": 0.3},
            },
        ) as aligner:
            aligned, report = aligner.align(
                {
                    "rna": pd.DataFrame({"sample_id": ["s1"], "A": [1], "B": [2]}),
                    "cnv": pd.DataFrame({"sample_id": ["s1"], "A": [3], "B": [4]}),
                    "snv": pd.DataFrame({"sample_id": ["s1"], "A": [5], "B": [6]}),
                    "meth": pd.DataFrame({"sample_id": ["s1"], "A": [7], "B": [8]}),
                }
            )

            self.assertEqual(list(aligned.keys()), ["rna", "cnv", "snv", "meth"])
            self.assertEqual(aligned["rna"].to_dict("records"), [
                {"A": 1, "B": 2, "C": 30},
            ])
            self.assertEqual(aligned["cnv"].to_dict("records"), [
                {"A": 3, "B": 4, "C": 300},
            ])
            self.assertEqual(aligned["snv"].to_dict("records"), [
                {"A": 5, "B": 6, "C": 1},
            ])
            self.assertEqual(aligned["meth"].to_dict("records"), [
                {"A": 7, "B": 8, "C": 0.3},
            ])
            self.assertEqual(report["modalities"], ["rna", "cnv", "snv", "meth"])
            self.assertEqual(report["sample_counts"], {
                "rna": 1,
                "cnv": 1,
                "snv": 1,
                "meth": 1,
            })

    def test_rejects_missing_uploaded_modality(self):
        with multiomics_aligner_for(
            ["A"],
            {
                "rna": {"A": 1},
                "cnv": {"A": 1},
                "snv": {"A": 1},
                "meth": {"A": 1},
            },
        ) as aligner:
            with self.assertRaisesRegex(ValueError, "Missing uploaded"):
                aligner.align(
                    {
                        "rna": pd.DataFrame({"A": [1]}),
                        "cnv": pd.DataFrame({"A": [1]}),
                        "snv": pd.DataFrame({"A": [1]}),
                    }
                )

    def test_rejects_mismatched_sample_counts(self):
        with multiomics_aligner_for(
            ["A"],
            {
                "rna": {"A": 1},
                "cnv": {"A": 1},
                "snv": {"A": 1},
                "meth": {"A": 1},
            },
        ) as aligner:
            with self.assertRaisesRegex(ValueError, "same number of samples"):
                aligner.align(
                    {
                        "rna": pd.DataFrame({"A": [1, 2]}),
                        "cnv": pd.DataFrame({"A": [1]}),
                        "snv": pd.DataFrame({"A": [1]}),
                        "meth": pd.DataFrame({"A": [1]}),
                    }
                )


class aligner_for:
    def __init__(
        self,
        expected_genes: list[str],
        medians: dict[str, float],
        min_match_rate: float = 0.0,
    ) -> None:
        self.expected_genes = expected_genes
        self.medians = medians
        self.min_match_rate = min_match_rate
        self.temp_dir = tempfile.TemporaryDirectory()

    def __enter__(self) -> GeneExpressionAligner:
        directory_path = Path(self.temp_dir.name)
        expected_path = directory_path / "expected_geo_genes.csv"
        medians_path = directory_path / "geo_gene_medians.csv"

        pd.DataFrame({"gene": self.expected_genes}).to_csv(expected_path, index=False)
        pd.DataFrame(
            {
                "gene": list(self.medians.keys()),
                "median": list(self.medians.values()),
            }
        ).to_csv(medians_path, index=False)

        return GeneExpressionAligner(
            expected_genes_path=expected_path,
            medians_path=medians_path,
            min_match_rate=self.min_match_rate,
        )

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.temp_dir.cleanup()


class multiomics_aligner_for:
    def __init__(
        self,
        expected_genes: list[str],
        medians_by_modality: dict[str, dict[str, float]],
        min_match_rate: float = 0.0,
    ) -> None:
        self.expected_genes = expected_genes
        self.medians_by_modality = medians_by_modality
        self.min_match_rate = min_match_rate
        self.temp_dir = tempfile.TemporaryDirectory()

    def __enter__(self) -> MultiOmicsGeneExpressionAligner:
        directory_path = Path(self.temp_dir.name)
        expected_path = directory_path / "expected_geo_genes.csv"
        pd.DataFrame({"gene": self.expected_genes}).to_csv(expected_path, index=False)

        medians_paths = {}
        for modality, medians in self.medians_by_modality.items():
            medians_path = directory_path / f"{modality}_gene_medians.csv"
            pd.DataFrame(
                {
                    "gene": list(medians.keys()),
                    "median": list(medians.values()),
                }
            ).to_csv(medians_path, index=False)
            medians_paths[modality] = medians_path

        return MultiOmicsGeneExpressionAligner(
            expected_genes_path=expected_path,
            medians_paths=medians_paths,
            min_match_rate=self.min_match_rate,
        )

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
