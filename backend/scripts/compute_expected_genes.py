import os
import pandas as pd


def extract_genes_from_headers(input_file, output_file, sample_id_col=0):
    """Extracts gene names from the column headers of an expression matrix.

    Parameters:
    - input_file: Path to the expression data (csv, tsv, txt, xlsx).
    - output_file: Path where the output gene list will be saved.
    - sample_id_col: The index or name of the sample ID column to skip (default is 0).
    """
    print(f"Reading {input_file}...")

    # 1. load just the headers (saves memory for large matrices)
    df_headers = pd.read_csv(input_file, nrows=0)

    # 2. Get all column names
    all_columns = df_headers.columns.tolist()

    # 3. Remove the Sample ID column name so it isn't counted as a gene
    if isinstance(sample_id_col, int):
        # Remove by index position
        if 0 <= sample_id_col < len(all_columns):
            all_columns.pop(sample_id_col)
    elif sample_id_col in all_columns:
        # Remove by explicit string name
        all_columns.remove(sample_id_col)

    # 4. Clean up the gene list (remove whitespace, drop duplicates)
    gene_list = [str(g).strip() for g in all_columns if pd.notna(g)]
    gene_list = list(dict.fromkeys(gene_list))  # Removes duplicates preserving order

    # 5. Create DataFrame and save
    output_df = pd.DataFrame({"gene": gene_list})
    output_df.to_csv(output_file, index=False)

    print(
        f"Success! Extracted {len(output_df)} unique genes from headers into '{output_file}'."
    )


# --- HOW TO RUN IT ---
if __name__ == "__main__":
    # Replace these with your actual file paths
    INPUT_DATA = "backend\\model_inputs\\breast\\geo_full_data.csv"
    OUTPUT_DATA = "backend\\model_inputs\\breast\\expected_geo_genes.csv"

    # The script assumes your first column (index 0) is something like 'Sample_ID'.
    # It will skip this column and treat all other headers as genes.
    SAMPLE_COL = 0

    extract_genes_from_headers(INPUT_DATA, OUTPUT_DATA, SAMPLE_COL)