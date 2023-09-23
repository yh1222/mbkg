# STITCH转换的加速版本
import os
os.environ['NUMEXPR_MAX_THREADS'] = '272'

from pyMeSHSim.metamapWrap.MetamapInterface import MetaMap
import pandas as pd
import numpy as np
from pandarallel import pandarallel
# import csv

cg_df = pd.read_csv("/data/1011/ZYH/mgkg/database/STITCH/cg_relation.csv", sep='\t', header=None)
cg_df.replace('ENTREZ:NA', np.nan, inplace=True)
cg_df.dropna(axis=0, how='any', inplace=True)
cg_df.rename(columns={0: 'CID', 1: 'ENTREZ'}, inplace=True)
print('cg_df loading completed.')

match_df = pd.read_csv('/data/1011/ZYH/mgkg/database/STITCH/CID_alias.csv', sep='\t', header=None, names=['CID', 'alias'])
print('match_df loading completed.')

# 'chem', 'chvf', 'chvs', 'inch', 'orch'
metamap = MetaMap(path="/data/1011/ZYH/MetaMap/public_mm/bin/metamap16")


def switch(alias):
    concept = metamap.runMetaMap(semantic_types=['chem', 'chvf', 'chvs', 'inch', 'orch'], text=alias, source=["MSH"])
    # print(alias)
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


# speed up
pandarallel.initialize(progress_bar=False, nb_workers=24)
match_df['MeSH'] = match_df['alias'].parallel_apply(switch)
match_df.drop('alias', axis=1, inplace=True)
print('Convertion completed.')

match_df.dropna(axis=0, how='any', inplace=True)
match_df.drop_duplicates(subset=['CID'], inplace=True)
match_df.to_csv('/data/1011/ZYH/mgkg/data/structure/STITCH/meshid.csv', sep='\t', header=0, index=0)
print('Converted file is saved')

# split rows
match_df = match_df.drop(['MeSH'], axis=1).join(match_df['MeSH'].str.split(',', expand=True).stack().reset_index(level=1, drop=True).rename('MeSH'))

triplets_df = pd.merge(match_df, cg_df, on='CID')[['MeSH', 'ENTREZ']]
triplets_df.insert(loc=1, column='relation', value='chemical:gene:STITCH')
triplets_df.drop_duplicates(inplace=True)
triplets_df.to_csv('/data/1011/ZYH/mgkg/data/structure/STITCH/STITCH_tripletes2.csv', sep='\t', header=0, index=0)
print('ALL Done.')
