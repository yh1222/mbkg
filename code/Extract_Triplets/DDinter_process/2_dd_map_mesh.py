import pandas as pd
import numpy as np

mesh_dict = np.load("/data/1011/ZYH/mgkg/database/MESH/items_dict.npy", allow_pickle=True).item()
mesh_data = pd.DataFrame.from_dict(mesh_dict, orient='index')
mesh_data.reset_index(inplace=True)
mesh_data.rename(columns={'index': 'name', 0: 'mesh'}, inplace=True)

data = pd.read_csv('/data/1011/ZYH/mgkg/code/DDinter_process/ddinter_triple.csv', sep='\t', header=0)

# 先换头实体
match_df = pd.merge(data, mesh_data, left_on='Drug_A', right_on='name')
match_df.drop(['Drug_A', 'name'], axis=1, inplace=True)
match_df = match_df['mesh', 'Level', 'Drug_B']
match_df = match_df[['mesh', 'Level', 'Drug_B']]
match_df.rename(columns={'mesh': 'Drug_A'}, inplace=True)
# 再换尾实体
match_df = pd.merge(match_df, mesh_data, left_on='Drug_B', right_on='name')
match_df.drop(['Drug_B', 'name'], axis=1, inplace=True)
match_df.rename(columns={'mesh': 'Drug_B'}, inplace=True)
# 修正格式
match_df.drop_duplicates(inplace=True)
match_df.insert(loc=0, column='str', value='MESH:')
match_df['Drug_A'] = match_df['str'] + match_df['Drug_A']
match_df['Drug_B'] = match_df['str'] + match_df['Drug_B']
match_df['str'] = 'DDinter:'
match_df['Level'] = match_df['str'] + match_df['Level']
match_df.drop('str', axis=1, inplace=True)
# 保存
match_df.to_csv("/data/1011/ZYH/mgkg/data/structure/DDinter/DDinter_triplets.csv", sep='\t', header=0, index=0)
