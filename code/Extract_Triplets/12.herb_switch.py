import pandas as pd

herb_df = pd.read_table("/data/1011/ZYH/mgkg/database/TCMID/herb.tsv", sep='\t', header=0)
herb_df.dropna(axis=0, how='any', subset=['Pinyin Name', 'Indication'], inplace=True)
herb_df = herb_df[['Pinyin Name', 'Indication']]
herb_df.reset_index(drop=True, inplace=True)

# 分行
# 下面一定要用‘herb_df.drop(['Indication'], axis=1)’，因为这是原链接，仍然是DataFrame
# 如果提取出一列就变成了Series，而Series是没有join方法的
herb_df = herb_df.drop(['Indication'], axis=1).join(herb_df['Indication'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).rename('Indication'))

# 保存原始三元组文件
herb_df.insert(loc=1, column='Relation', value='chemical:disease:T')
print('Saving unconverted triplets...')
herb_df.to_csv('/data/1011/ZYH/mgkg/database/TCMID/herb_indication.csv', sep='\t', header=0, index=0)

# 保存Indications
herb_df.reset_index(drop=True, inplace=True)
for index, row in herb_df.iterrows():
    # print(herb_df.loc[index, 'Indication'])
    prev = herb_df.loc[index, 'Indication']
    curr = str(index + 1) + '|' + str(prev)
    herb_df.loc[index, 'Indication'] = curr
    # print(herb_df.loc[index, 'Indication'])
print('Saving indications...')
herb_df['Indication'].to_csv('/data/1011/ZYH/mgkg/database/TCMID/indications.txt', sep='\t', header=0, index=0)

# 接下来使用pyMeSHSIm提供的pipeline.py完成转换
# python ./pipeline.py textParse /data/1011/ZYH/MetaMap/public_mm/bin/metamap16 /data/1011/ZYH/mgkg/database/TMCID/indications.txt /data/1011/ZYH/mgkg/database/TMCID/ --source=MSH --short
