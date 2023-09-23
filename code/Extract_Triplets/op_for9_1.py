# 去除GNBR三元组中的重复项
# 将缺少MESH标识的实体加上"MESH:", (也许也有缺少CHEBI或OMIM的实体, 处理时也考虑进去吧)
# 为基因实体前面加上'ENTREZ:'
# 去除基因实体后面的(Tax:xxxxx)
import pandas as pd
import re


def process(file_path):
    df = pd.read_csv(file_path, sep='\t', header=None, on_bad_lines='skip')
    df.drop_duplicates(inplace=True)
    if 'chemical_disease' in file_path:
        for index, row in df.iterrows():
            df.loc[index, 1] = 'chemical:disease:' + str(row[1])
            head = row[0].split(':')
            tail = row[2].split(':')
            if len(head) < 2:
                if re.match('^\D', head[0]):
                    df.loc[index, 0] = 'MESH:' + head[0]
                else:
                    df.loc[index, 0] = 'CHEBI:' + head[0]
            if len(tail) < 2:
                if re.match('^\D', tail[0]):
                    df.loc[index, 2] = 'MESH:' + tail[0]
                else:
                    df.loc[index, 2] = 'OMIM:' + tail[0]
    if 'chemical_gene' in file_path:
        for index, row in df.iterrows():
            df.loc[index, 1] = 'chemical:gene:' + str(row[1])
            df.loc[index, 2] = 'ENTREZ:' + str(row[2])
            head = row[0].split(':')
            tail = row[2].split('(')
            if len(head) < 2:
                if re.match('^\D', head[0]):
                    df.loc[index, 0] = 'MESH:' + head[0]
                else:
                    df.loc[index, 0] = 'CHEBI:' + head[0]
            if len(tail) > 1:
                df.loc[index, 2] = tail[0]
    if 'gene_disease' in file_path:
        for index, row in df.iterrows():
            df.loc[index, 1] = 'gene:disease:' + str(row[1])
            df.loc[index, 0] = 'ENTREZ:' + str(row[0])
            head = row[0].split('(')
            tail = row[2].split(':')
            if len(head) > 1:
                df.loc[index, 0] = head[0]
            if len(tail) < 2:
                if re.match('^\D', tail[0]):
                    df.loc[index, 2] = 'MESH:' + tail[0]
                else:
                    df.loc[index, 2] = 'OMIM:' + tail[0]
    if 'gene_gene' in file_path:
        for index, row in df.iterrows():
            df.loc[index, 1] = 'gene:gene:' + str(row[1])
            df.loc[index, 0] = 'ENTREZ:' + str(row[0])
            df.loc[index, 2] = 'ENTREZ:' + str(row[2])
            head = row[0].split('(')
            tail = row[2].split('(')
            if len(head) > 1:
                df.loc[index, 0] = head[0]
            if len(tail) > 1:
                df.loc[index, 2] = tail[0]
    df.to_csv(file_path, sep='\t', index=0, header=0)


def main():
    files = ['chemical_disease_triplets.csv', 'chemical_gene_triplets.csv', 'gene_disease_triplets.csv', 'gene_gene_triplets.csv']
    # files = ['test.csv']
    dir_path = '/data/1011/ZYH/mgkg/data/structure/GNBR/'
    # dir_path = 'D:/projects/MGKG/Python_programs/'
    for file in files:
        file_path = dir_path + file
        process(file_path)


if __name__ == '__main__':
    main()
