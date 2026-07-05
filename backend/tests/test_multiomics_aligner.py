import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.gene_expression_aligner import MultiOmicsGeneExpressionAligner


class MultiOmicsGeneExpressionAlignerTest(unittest.TestCase):
    def test_aligns_each_modality_in_contract_order_and_fills_own_medians(self):
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
                    "rna": pd.DataFrame(
                        {"sample_id": ["s1"], "B": [2], "A": [1]},
                    ),
                    "cnv": pd.DataFrame(
                        {"sample_id": ["s1"], "B": [4], "A": [3]},
                    ),
                    "snv": pd.DataFrame(
                        {"sample_id": ["s1"], "B": [6], "A": [5]},
                    ),
                    "meth": pd.DataFrame(
                        {"sample_id": ["s1"], "B": [8], "A": [7]},
                    ),
                }
            )

            self.assertEqual(list(aligned.keys()), ["rna", "cnv", "snv", "meth"])
            for modality_frame in aligned.values():
                self.assertEqual(list(modality_frame.columns), ["A", "B", "C"])

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
            self.assertEqual(report["reports"]["rna"]["missing_gene_names"], ["C"])

    def test_aligns_row_oriented_uploads_for_all_modalities(self):
        with multiomics_aligner_for(
            ["A", "B"],
            {
                "rna": {"A": 10, "B": 20},
                "cnv": {"A": 100, "B": 200},
                "snv": {"A": 0, "B": 1},
                "meth": {"A": 0.1, "B": 0.2},
            },
        ) as aligner:
            upload = pd.DataFrame(
                {
                    "gene": [" a ", "b"],
                    "sample_1": [1, 2],
                    "sample_2": [3, 4],
                }
            )

            aligned, report = aligner.align(
                {
                    "rna": upload,
                    "cnv": upload,
                    "snv": upload,
                    "meth": upload,
                }
            )

            self.assertEqual(aligned["rna"].to_dict("records"), [
                {"A": 1, "B": 2},
                {"A": 3, "B": 4},
            ])
            self.assertEqual(report["sample_counts"], {
                "rna": 2,
                "cnv": 2,
                "snv": 2,
                "meth": 2,
            })
            self.assertEqual(
                report["reports"]["rna"]["orientation"],
                "genes_as_rows",
            )

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

    def test_rejects_missing_medians_path_for_modality(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            expected_path = directory_path / "expected_geo_genes.csv"
            pd.DataFrame({"gene": ["A"]}).to_csv(expected_path, index=False)

            medians_paths = {}
            for modality in ("rna", "cnv", "snv"):
                medians_path = directory_path / f"{modality}_gene_medians.csv"
                pd.DataFrame({"gene": ["A"], "median": [1]}).to_csv(
                    medians_path,
                    index=False,
                )
                medians_paths[modality] = medians_path

            with self.assertRaisesRegex(ValueError, "Missing medians paths"):
                MultiOmicsGeneExpressionAligner(
                    expected_genes_path=expected_path,
                    medians_paths=medians_paths,
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
