import os
os.environ['NUMEXPR_MAX_THREADS'] = '272'
from pyMeSHSim.metamapWrap.MetamapInterface import MetaMap
import pandas as pd
import numpy as np
from pandarallel import pandarallel


mesh_dict = np.load("/data/1011/ZYH/mgkg/database/MESH/items_dict.npy", allow_pickle=True).item()
mesh_data = pd.DataFrame.from_dict(mesh_dict, orient='index')
mesh_data.reset_index(inplace=True)
mesh_data.rename(columns={'index': 'name', 0: 'mesh'}, inplace=True)
data = pd.read_csv("/data/1011/ZYH/mgkg/code/DrugBank_process/drug_entrez.csv", sep='\t', header=None, names=['id', 'drug', 'rel', 'target'])

# 精确匹配
match_df = pd.merge(data, mesh_data, left_on='drug', right_on='name', how='left')
exact_df = match_df.dropna().drop(['id', 'drug', 'name'], axis=1)[['mesh', 'rel', 'target']]
exact_df['mesh'] = 'MESH:' + exact_df['mesh']

# 模糊匹配
unmap_df = match_df[match_df.isnull().T.any()].drop(['id', 'name', 'mesh'], axis=1)
metamap = MetaMap(path="/data/1011/ZYH/MetaMap/public_mm/bin/metamap16")


def switch(drug):
    concept = metamap.runMetaMap(semantic_types=['chem', 'chvf', 'chvs', 'inch', 'orch'], text=drug, source=["MSH"])
    # print(drug)
    if len(concept) == 0:
        return np.nan
    else:
        i = 0
        for item in concept:
            if i == 0:
                id = 'MESH:' + str(item['MeSHID'])
            else:
                id += ',' + 'MESH:' + str(item['MeSHID'])
            i += 1
        return id


pandarallel.initialize(progress_bar=False, nb_workers=24)
unmap_df['mesh'] = unmap_df['drug'].parallel_apply(switch)
unmap_df.drop('drug', axis=1, inplace=True)
unmap_df.dropna(axis=0, how='any', inplace=True)
unmap_df = unmap_df.drop(['mesh'], axis=1).join(unmap_df['mesh'].str.split(',', expand=True).stack().reset_index(level=1, drop=True).rename('mesh'))
unmap_df = unmap_df[['mesh', 'rel', 'target']]

# 总表
match_df = pd.concat((exact_df, unmap_df))
match_df.drop_duplicates(inplace=True)
match_df['rel'] = 'DrugBank:' + match_df['rel']
match_df['target'] = 'ENTREZ:' + match_df['target'].astype(str)
match_df.to_csv("/data/1011/ZYH/mgkg/data/structure/DrugBank/DrugBank_triplets.csv", sep='\t', header=0, index=0)
