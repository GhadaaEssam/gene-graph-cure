import pandas as pd

# 1. Load your data
# Assuming your matrix has the IDs as the first row (headers)
matrix = pd.read_csv('backend\\model_inputs\\liver\\liver_geo_train_split.csv', index_col=0) 
mapping_df = pd.read_csv('backend\\model_inputs\\liver\\anchor_genes.csv')

# 2. Create a mapping dictionary {id: gene_name}
# Ensure strings are used to avoid indexing issues
mapping_dict = dict(zip(mapping_df['id'].astype(str), mapping_df['gene']))

# 3. Rename the columns
# .rename() ignores IDs that aren't in the mapping dictionary
matrix.rename(columns=mapping_dict, inplace=True)

# 4. Save the result
matrix.to_csv(
    'backend/model_inputs/liver/matrix_with_gene_names.csv', 
    chunksize=5000  # Writes in chunks to manage memory
)