# 使用命令：awk '$3 !~ /[0-9]{4,}/' chemical.aliases.v5.0.tsv > filter_aliase.csv 删除包含连续4个数字的别名
# 不可用source: 2322|708|NIST|10590|NextBio|1137|940|MMDB|1085|1100|MolPort|824|LeadScope|ChEBI|ChemIDplus|BIND
# awk '$4 !~ /不可用source/' filter_aliase.csv > filtered_alias.csv
# 因为总是搞混，就把filter_aliase.csv删了
# 从头开始命令为：awk '$3 !~ /[0-9]{4,}/' chemical.aliases.v5.0.tsv | awk '$4 !~ /不可用source/' > filtered_alias.csv
import os
os.environ['NUMEXPR_MAX_THREADS'] = '272'

from pyMeSHSim.metamapWrap.MetamapInterface import MetaMap
import pandas as pd
import numpy as np
# import csv

alias_df = pd.read_csv("/data/1011/ZYH/mgkg/database/STITCH/filtered_alias.csv", sep='\t', header=0, dtype={'source': object})
alias_df.rename(columns={'flat_chemical': 'CIDm', 'stereo_chemical': 'CIDs'}, inplace=True)
print('alias_df loading completed.')

cg_df = pd.read_csv("/data/1011/ZYH/mgkg/database/STITCH/cg_relation.csv", sep='\t', header=None)
cg_df.replace('ENTREZ:NA', np.nan, inplace=True)
cg_df.dropna(axis=0, how='any', inplace=True)
cg_df.rename(columns={0: 'CID', 1: 'ENTREZ'}, inplace=True)
print('cg_df loading completed.')

cid = pd.DataFrame(cg_df['CID'].drop_duplicates())

stitch_m = pd.merge(cid, alias_df, left_on='CID', right_on='CIDm')[['CID', 'alias']]
stitch_s = pd.merge(cid, alias_df, left_on='CID', right_on='CIDs')[['CID', 'alias']]
match_df = pd.concat([stitch_m, stitch_s], ignore_index=True)
match_df.drop_duplicates(inplace=True)
match_df = match_df[~match_df['alias'].str.contains('\|')]
print('Alias matching completed.')

match_df.to_csv('/data/1011/ZYH/mgkg/database/STITCH/CID_alias.csv', sep='\t', header=0, index=0)
print('Alias matching file is saved.')

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


match_df['MeSH'] = match_df['alias'].apply(switch)
match_df.drop('alias', axis=1, inplace=True)
print('Convertion completed.')

match_df.dropna(axis=0, how='any', inplace=True)
match_df.drop_duplicates(subset=['CID'], inplace=True)
match_df = match_df.drop(['alias'], axis=1).join(match_df['alias'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).rename('MeSH'))

triplets_df = pd.merge(match_df, cg_df, on='CID')[['MeSH', 'ENTREZ']]
match_df.insert(loc=1, column='relation', value='chemical:gene:STITCH')
match_df.to_csv('/data/1011/ZYH/mgkg/data/structure/STITCH/STITCH_tripletes.csv', sep='\t', header=0, index=0)
print('ALL Done.')
