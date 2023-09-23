from fuzzywuzzy import process
import pandas as pd
import numpy as np
import csv


# 数据框模糊匹配(只选取匹配得分大于等于75的项)
def fuzzy_match(x, standard_names):
    compare = process.extractOne(x, standard_names)
    if compare[1] >= 75:
        return str(compare[0]) + '::' + str(compare[1])
    return np.nan


# 设置空间大小, 因为chemical.aliases.v5.0.tsv文件非常大
csv.field_size_limit(500 * 1024 * 1024)

# 读取目标转换文件和别名文件
aliase_file = "/data/1011/ZYH/mgkg/database/STITCH/chemical.aliases.v5.0.tsv"
stitch_file = "/data/1011/ZYH/mgkg/database/STITCH/cg_relation.csv"
aliase_df = pd.read_table(aliase_file, sep='\t', header=0, engine='python', quoting=csv.QUOTE_NONE)
stitch_df = pd.read_csv(stitch_file, sep='\t', header=None)
# 规范化数据框
stitch_df.replace('ENTREZ:NA', np.nan, inplace=True)
stitch_df.dropna(axis=0, how='any', inplace=True)
aliase_df.rename(columns={'flat_chemical': 'CIDm', 'stereo_chemical': 'CIDs'}, inplace=True)
stitch_df.rename(columns={0: 'CID', 1: 'ENTREZ'}, inplace=True)
# 去除stitch中的重复的化学实体ID
stitch_filter_df = stitch_df.drop_duplicates(subset='CID')
stitch_filter_df.reset_index(drop=True, inplace=True)
# 去除alias部分ID数据, 保留更多的名称数据
pattern = r'\d{4,}'
aliase_df['alias'].str.contains(pattern, regex=True)
aliase_df.drop(aliase_df[aliase_df['alias'].str.contains(pattern, regex=True) == True].index, inplace=True)
aliase_df.reset_index(drop=True, inplace=True)
# 保留alias文件中每组化学ID前10个别名
aliase_df = aliase_df.groupby(['CIDm', 'CIDs']).head(10)
aliase_df.reset_index(drop=True, inplace=True)
# 获取和stitch文件中匹配的别名数据
stitch_m = pd.merge(stitch_filter_df, aliase_df, left_on='CID', right_on='CIDm')[['CID', 'alias']]
stitch_s = pd.merge(stitch_filter_df, aliase_df, left_on='CID', right_on='CIDs')[['CID', 'alias']]
alias_filter_df = pd.concat([stitch_m, stitch_s], ignore_index=True)
# 读取mesh数据并转换为数据框
mesh = np.load('/data/1011/ZYH/mgkg/database/MESH/items_dict.npy', allow_pickle=True).item()
mesh_df = pd.DataFrame.from_dict(mesh, orient='Index')
mesh_df.reset_index(inplace=True)
mesh_df.rename(columns={'index': 'alias', 0: 'mesh_id'}, inplace=True)
# 模糊匹配
alias_filter_df['keys'] = alias_filter_df['alias'].apply(lambda x: fuzzy_match(x, mesh_df['alias']))
alias_filter_df.dropna(inplace=True)
alias_filter_df = pd.concat([alias_filter_df, alias_filter_df['keys'].str.split('::', expand=True)], axis=1)
alias_filter_df.reset_index(drop=True, inplace=True)
alias_filter_df.drop(columns=['keys', 'alias'], axis=1, inplace=True)
alias_filter_df.rename(columns={0: 'name', 1: 'score'}, inplace=True)
# 分组取得分最高的行(即最高匹配度)
alias_filter_df['score'] = pd.to_numeric(alias_filter_df['score'], errors='raise')
corres_df = alias_filter_df.groupby('CID').apply(lambda t: t[t['score'] == t['score'].max()])
# 合并同类项
corres_df = corres_df[['CID', 'name']].reset_index(drop=True)
corres_df = pd.merge(corres_df, mesh_df, left_on='name', right_on='alias')
corres_df.drop(['name', 'alias'], axis=1, inplace=True)
# 最后的整合
final_df = pd.merge(stitch_df, corres_df, on='CID')
final_df.drop('CID', axis=1, inplace=True)
final_df = final_df[['mesh_id', 'ENTREZ']]
final_df.insert(loc=1, column='relation', value='chemical:gene:unknown')
final_df.insert(loc=0, column='string', value='MESH:')
new_line = final_df['string'].str.cat(final_df['mesh_id'], sep='').copy()
final_df.insert(loc=0, column='MESH', value=new_line)
final_df = pd.DataFrame(final_df)  # 因为有个奇怪的警告, 太晚了脑子不太清醒, 所以直接用了暴力的方法去除警告
final_df.drop(['string', 'mesh_id'], axis=1, inplace=True)
# 保存
final_df.to_csv('/data/1011/ZYH/mgkg/data/structure/STITCH/chemical_gene_triplets.csv', sep='\t', header=False, index=False)
