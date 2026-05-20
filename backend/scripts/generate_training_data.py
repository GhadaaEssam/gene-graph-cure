import pandas as pd

def get_raw_geo_train(data_geo_path: str, test_anchor_path: str, output_path: str = 'result/raw_X_train.csv'):
    """
    Extracts raw training rows from data_geo using the saved test_anchor split.
    
    Args:
        data_geo_path:    Path to the original data_geo CSV file
        test_anchor_path: Path to the saved test_anchor CSV (result/test_anchor.csv)
        output_path:      Where to save the raw training data
    """
    # Load inputs
    data_geo   = pd.read_csv(data_geo_path, index_col=0)
    test_anchor = pd.read_csv(test_anchor_path, index_col=0).squeeze()

    # Derive train indices
    all_indices  = set(data_geo.index.tolist())
    test_indices = set(test_anchor.tolist())
    train_indices = list(all_indices - test_indices)

    # Extract raw train rows (no transformation)
    raw_X_train = data_geo.loc[train_indices]

    # Save
    raw_X_train.to_csv(output_path, index=True)
    print(f"Saved {len(raw_X_train)} training rows to {output_path}")

    return raw_X_train


if __name__ == "__main__":
    raw_X_train = get_raw_geo_train(
        data_geo_path    = 'backend\scripts\data\1-Breast Cancer TFAC_result_test_rank.csv',      # <- change to your path
        test_anchor_path = 'backend\scripts\result\br_test_anchor.csv',
        output_path      = 'backend\model_inputs\breast\br_raw_X_train.csv'
    )