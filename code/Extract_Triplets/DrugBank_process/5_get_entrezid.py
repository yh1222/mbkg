import pandas as pd
map_data = pd.read_csv(
    "/data/1011/ZYH/mgkg/code/DrugBank_process/symbol_entrezid.csv",
    sep=',', header=0, names=['id', 'symbol', 'entrez'])
data = pd.read_csv(
    "/data/1011/ZYH/mgkg/code/DrugBank_process/protein.csv",
    sep='\t', header=None, names=['drug', 'rel', 'target'])
data.drop_duplicates(inplace=True)
data.insert(loc=0, column='id', value=range(1, len(data)+1))
match_df = pd.merge(data, map_data, left_on='target', right_on='symbol')
match_df.drop(['target', 'id_y', 'symbol'], axis=1, inplace=True)
match_df.to_csv('/data/1011/ZYH/mgkg/code/DrugBank_process/drug_entrez.csv', sep='\t', header=0, index=0)
