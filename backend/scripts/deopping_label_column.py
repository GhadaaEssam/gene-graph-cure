import pandas as pd

# 1. Load the data
file_path = 'backend/model_inputs/liver/geo_train_split.csv'
file_path2 = 'backend/model_inputs/ovarian/geo_train_split.csv'
file_path3 = 'backend/model_inputs/immunotherapy/geo_train_split.csv'

for file_path in [file_path, file_path2, file_path3]:
    df = pd.read_csv(file_path, index_col=0)
    df.drop(df.columns[0], axis=1, inplace=True)
    df.to_csv(file_path)
    print(f"Successfully updated {file_path}. Second column removed.")
