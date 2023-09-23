# 将CHEBI和OMIM条目去除
# 去除多余的'ENTREZ:'
import pandas as pd

path = '/data/1011/ZYH/mgkg/data/structure/GNBR/'
files = ["chemical_disease_triplets.csv", "chemical_gene_triplets.csv", "gene_disease_triplets.csv", "gene_gene_triplets.csv"]

for file in files:
    file = path + file
    name = file.split('/')[-1].split('.')[0]
    print(name)
    remove_id = []
    if name == 'chemical_gene_triplets':
        df = pd.read_csv(file, sep='\t', header=None, names=['c', 'r', 'g'])
        for index, row in df.iterrows():
            head = row['c'].split(':')
            tail = row['g'].split(':')
            if head[0] == 'CHEBI':
                remove_id.append(index)
            df.loc[index, 'g'] = tail[0] + ':' + tail[-1]
        df.drop(remove_id, inplace=True)
    if name == 'chemical_disease_triplets':
        df = pd.read_csv(file, sep='\t', header=None, names=['c', 'r', 'd'])
        for index, row in df.iterrows():
            head = row['c'].split(':')
            tail = row['d'].split(':')
            if head[0] == 'CHEBI' or tail[0] == 'OMIM':
                remove_id.append(index)
        df.drop(remove_id, inplace=True)
    if name == 'gene_disease_triplets':
        df = pd.read_csv(file, sep='\t', header=None, names=['g', 'r', 'd'])
        for index, row in df.iterrows():
            head = row['g'].split(':')
            tail = row['d'].split(':')
            if tail[0] == 'OMIM':
                remove_id.append(index)
            df.loc[index, 'g'] = head[0] + ':' + head[-1]
        df.drop(remove_id, inplace=True)
    if name == 'gene_gene_triplets':
        df = pd.read_csv(file, sep='\t', header=None, names=['g1', 'r', 'g2'])
        for index, row in df.iterrows():
            head = row['g1'].split(':')
            tail = row['g2'].split(':')
            df.loc[index, 'g1'] = head[0] + ':' + head[-1]
            df.loc[index, 'g2'] = tail[0] + ':' + tail[-1]
    save_path = '/data/1011/ZYH/mgkg/data/structure/GNBR/' + name + '2.csv'
    df.to_csv(save_path, sep='\t', index=False, header=False)
