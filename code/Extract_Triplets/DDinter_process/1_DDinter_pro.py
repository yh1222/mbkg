import pandas as pd
from pathlib import Path
dir_path = '/data/1011/ZYH/mgkg/database/DDinter/'
file_paths = [f for f in Path(dir_path).glob('*.csv') if Path(f).is_file()]
save_path = "/data/1011/ZYH/mgkg/code/DDinter_process/ddinter_triple.csv"
for path in file_paths:
    data = pd.read_table(path, header='infer', sep=',', names=['DDInterID_A', 'Drug_A', 'DDInterID_B', 'Drug_B', 'Level'])
    DDA = data['Drug_A']
    DDB = data['Drug_B']
    rel = data['Level']
    result = []
    for i in range(len(data)):
        result.append(f'{DDA[i]}\t{rel[i]}\t{DDB[i]}\n')
    with open(save_path, 'a') as f:
        f.writelines(result)
