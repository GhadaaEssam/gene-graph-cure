from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_MODEL_INPUTS_DIR = Path(__file__).resolve().parents[1] / "model_inputs"
EXPECTED_GENES_FILENAME = "expected_geo_genes.csv"
TRAINING_DATA_FILENAME = "ov_raw_X_train.csv" # geo data
ANCHOR_GENES_FILENAME = "anchor_genes.csv"
OUTPUT_FILENAME = "geo_gene_medians.csv"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute per-gene training medians in each model contract order."
    )
    parser.add_argument(
        "--model-inputs-dir",
        type=Path,
        default=DEFAULT_MODEL_INPUTS_DIR,
        help="Directory containing per-cancer model input folders.",
    )
    parser.add_argument(
        "--cancer-type",
        action="append",
        help="Specific cancer folder to process. May be passed multiple times.",
    )
    args = parser.parse_args()

    model_dirs = _resolve_model_dirs(args.model_inputs_dir, args.cancer_type)
    if not model_dirs:
        raise SystemExit(f"No model input folders found in {args.model_inputs_dir}")

    for model_dir in model_dirs:
        output_path = compute_medians_for_model_dir(model_dir)
        print(f"Wrote {output_path}")


def compute_medians_for_model_dir(model_dir: Path) -> Path:
    expected_path = model_dir / EXPECTED_GENES_FILENAME
    training_path = model_dir / TRAINING_DATA_FILENAME
    anchor_path = model_dir / ANCHOR_GENES_FILENAME
    output_path = model_dir / OUTPUT_FILENAME

    _require_file(expected_path)
    _require_file(training_path)

    expected_genes = _read_expected_genes(expected_path)
    training_data = pd.read_csv(training_path)
    training_data = _drop_unnamed_index_columns(training_data)

    median_by_column = training_data.apply(pd.to_numeric, errors="coerce").median(
        axis=0,
        skipna=True,
    )

    source_columns = _resolve_source_columns(
        expected_genes=expected_genes,
        training_columns=[str(column) for column in training_data.columns],
        anchor_path=anchor_path,
    )

    missing_source_columns = [
        column for column in source_columns if column not in median_by_column.index
    ]
    if missing_source_columns:
        examples = ", ".join(missing_source_columns[:10])
        raise ValueError(
            f"{model_dir.name}: missing {len(missing_source_columns)} expected "
            f"training columns. Examples: {examples}"
        )

    output = pd.DataFrame(
        {
            "gene": expected_genes,
            "median": [median_by_column[column] for column in source_columns],
        }
    )
    output.to_csv(output_path, index=False)
    return output_path


def _resolve_model_dirs(model_inputs_dir: Path, cancer_types: list[str] | None) -> list[Path]:
    if cancer_types:
        return [model_inputs_dir / cancer_type for cancer_type in cancer_types]

    return sorted(
        path
        for path in model_inputs_dir.iterdir()
        if path.is_dir() and (path / EXPECTED_GENES_FILENAME).exists()
    )


def _read_expected_genes(path: Path) -> list[str]:
    expected = pd.read_csv(path)
    if list(expected.columns) != ["gene"]:
        raise ValueError(f"{path} must contain exactly one column named 'gene'")
    return expected["gene"].astype(str).tolist()


def _resolve_source_columns(
    expected_genes: list[str],
    training_columns: list[str],
    anchor_path: Path,
) -> list[str]:
    training_column_set = set(training_columns)
    if all(gene in training_column_set for gene in expected_genes):
        return expected_genes

    if not anchor_path.exists():
        return expected_genes

    anchor_genes = _drop_unnamed_index_columns(pd.read_csv(anchor_path))
    if not {"id", "gene"}.issubset(anchor_genes.columns):
        return expected_genes

    gene_to_id = dict(
        zip(
            anchor_genes["gene"].astype(str),
            anchor_genes["id"].astype(str),
        )
    )
    mapped_columns = [gene_to_id.get(gene, gene) for gene in expected_genes]
    if all(column in training_column_set for column in mapped_columns):
        return mapped_columns

    return expected_genes


def _drop_unnamed_index_columns(data: pd.DataFrame) -> pd.DataFrame:
    unnamed_columns = [
        column for column in data.columns if str(column).startswith("Unnamed:")
    ]
    return data.drop(columns=unnamed_columns)


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


if __name__ == "__main__":
    main()
