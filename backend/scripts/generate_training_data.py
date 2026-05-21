import pandas as pd
import numpy as np

def get_raw_geo_train(data_geo_path: str, label_geo_path: str, 
                      output_train_path: str = 'backend/scripts/data_ovarian/ov_raw_X_train.csv',
                      output_test_path: str  = 'backend/scripts/data_ovarian/ov_raw_X_test.csv',
                      k: int = 10, i: int = 4, seed: int = 4709):
    
    # 1. Load inputs
    data_geo  = pd.read_csv(data_geo_path, index_col=0)   # samples x genes
    label_geo = pd.read_csv(label_geo_path, index_col=0).squeeze()

    # 2. Shuffle data safely using pandas built-in sampling (reproduces the seed)
    # This avoids the .loc/.iloc mismatch entirely
    X = data_geo.sample(frac=1, random_state=seed)
    Y = label_geo.loc[X.index] # Keep labels perfectly aligned with the shuffled X

# 3. K-fold split (Pure Python/Pandas splitting to keep types intact)
    # This splits the index into k roughly equal parts
    fold_indices = np.array_split(np.arange(len(X)), k)

    X_train_list, Y_train_list = [], []
    X_test, Y_test = None, None

    for j in range(k):
        # Grab the specific rows for this fold using positional indexing (.iloc)
        X_part = X.iloc[fold_indices[j]]
        Y_part = Y.iloc[fold_indices[j]]

        if j == i:
            X_test = X_part
            Y_test = Y_part
        else:
            X_train_list.append(X_part)
            Y_train_list.append(Y_part)

    # Combine the training folds (Now safely processing pure DataFrames/Series!)
    X_train = pd.concat(X_train_list, axis=0)
    Y_train = pd.concat(Y_train_list, axis=0)

    # 4. Save using clean, safe forward slashes
    X_train.to_csv(output_train_path, index=True)
    X_test.to_csv(output_test_path,   index=True)
    pd.DataFrame(Y_train).to_csv('backend/scripts/data_ovarian/ov_raw_Y_train.csv', index=True)
    pd.DataFrame(Y_test).to_csv('backend/scripts/data_ovarian/ov_raw_Y_test.csv',   index=True)

    print(f"Total  samples : {len(data_geo)}")
    print(f"Train  samples : {len(X_train)}")
    print(f"Test   samples : {len(X_test)}")

    return X_train, X_test, Y_train, Y_test


if __name__ == "__main__":
    X_train, X_test, Y_train, Y_test = get_raw_geo_train(
        data_geo_path  = 'backend\\scripts\\data_ovarian\\1- Cisplatin resistance in ovarian cancer result_test_rank.csv', 
        label_geo_path = 'backend\\scripts\\data_ovarian\\cisplatin-resistant ovarian cancer sample_list.csv',   
    )