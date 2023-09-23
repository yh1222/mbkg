import pandas as pd


def omit_duplication(file_path):
    df = pd.read_table(file_path, sep='\t', header=None, on_bad_lines='skip')
    content = df.values.tolist()
    non_duplication = list(set(tuple(line) for line in content))
    new_data = [f'{element[0]}\t{element[1]}\t{element[2]}\t{element[3]}\t{element[4]}\n' for element in non_duplication]
    with open(file_path, 'w+') as f:
        for line in new_data:
            f.writelines(line)


files = ['chemical_disease_map.txt', 'chemical_gene_map.txt', 'gene_disease_map.txt', 'gene_gene_map.txt']
# files = ['gene_gene_map.txt']
# dir_path = 'D:/Projects/MGKG/mgkg_code/data/'
dir_path = '/data/1011/ZYH/mgkg/data/'
for file in files:
    file_path = dir_path + file
    omit_duplication(file_path)
