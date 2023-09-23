import pandas as pd

parse_df = pd.read_table('/data/1011/ZYH/mgkg/database/TCMID/parsing_result.txt', sep='\t', header=None)
herb_df = pd.read_csv('/data/1011/ZYH/mgkg/database/TCMID/herb_indication.csv', sep='\t', header=None, names=['Traditional_Medicine', 'Relationship', 'Disease'])
parse_df = parse_df[[1, 2]]
parse_df = parse_df.drop(2, axis=1).join(parse_df[2].str.split(',', expand=True).stack().reset_index(level=1, drop=True).rename('mesh'))
parse_df.columns = ['Disease', 'MeSH']
parse_df.drop_duplicates(inplace=True)
triplets_df = pd.merge(herb_df, parse_df, on='Disease')
triplets_df.drop('Disease', axis=1, inplace=True)
triplets_df.insert(loc=2, column='head', value='MESH:')
triplets_df['MESH'] = triplets_df['head'] + triplets_df['MeSH']
triplets_df.drop(['head', 'MeSH'], axis=1, inplace=True)
triplets_df.to_csv("/data/1011/ZYH/mgkg/data/structure/TCMID/tcmid.csv", sep='\t', header=0, index=0)
