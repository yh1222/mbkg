# 将蛋白转换为symbol，便于后续id转换
# all_carrier.csv, all_enzyme.csv, all_target.csv, all_trans.csv从drugbank上下载
import pandas as pd

carrier_path = "/data/1011/ZYH/mgkg/code/DrugBank_process/all_carrier.csv"
enzyme_path = "/data/1011/ZYH/mgkg/code/DrugBank_process/all_enzyme.csv"
target_path = "/data/1011/ZYH/mgkg/code/DrugBank_process/all_target.csv"
trans_path = "/data/1011/ZYH/mgkg/code/DrugBank_process/all_trans.csv"
# 接下来分别跑这四个文件(可以直接写成for循环)
# path = carrier_path
# path = enzyme_path
# path = target_path
path = trans_path
map_data = pd.read_csv(path, header='infer', sep=',',
                       names=['ID', 'Name', 'Gene_Name', 'GenBank_Protein_ID', 'GenBank_Gene_ID', 'UniProt_ID', 'Uniprot_Title', 'PDB_ID', 'GeneCard_ID', 'GenAtlas_ID', 'HGNC_ID', 'Species', 'Drug_IDs'])
map_gene = map_data['Name']
map_gene_name = map_data['Gene_Name']
dt_triple_path = "/data/1011/ZYH/mgkg/code/DrugBank_process/dt_triple.csv"
pro_data = pd.read_csv(dt_triple_path, header=None, sep='\t',
                       names=['drug', 'target', 'gene'])
pro_gene = pro_data['gene']
drug = pro_data['drug']
type = pro_data['target']
result = []
for i in range(len(pro_data)):
    for a in range(len(map_data)):
        if pro_gene[i] == map_gene[a] and map_gene_name[a] != '':
            print(pro_gene[i])
            result.append(f'{drug[i]}\t{type[i]}\t{map_gene_name[a]}\n')
with open('/data/1011/ZYH/mgkg/code/DrugBank_process/protein.csv', 'a') as f:
    f.writelines(result)
