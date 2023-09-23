import pandas as pd
from pathlib import Path


# 读取数据为DataFrame
def load_data(paths):
    '''paths is a list'''
    if not isinstance(paths, list):
        print('请确保输入的是一个路径列表')
    triplets_df = pd.DataFrame()
    for p in paths:
        temp_df = pd.read_csv(p, sep='\t', header=None)
        # print(temp_df.shape)
        triplets_df = pd.concat([triplets_df, temp_df], ignore_index=True)
    # print(triplets_df.shape)
    return triplets_df


# 设置目录路径
base_dir = Path.home() / 'mgkg' / 'data'

# 读取GNBR数据
GNBR_path = base_dir / 'structure' / 'GNBR'
GNBR_triplets_paths = [p for p in GNBR_path.glob('*triplets2.csv') if p.is_file()]
GNBR_df = load_data(GNBR_triplets_paths)  # (2949752, 3)

# 读取DrugBank数据
DrugBank_triplets_path = base_dir / 'structure' / 'DrugBank' / 'DrugBank_triplets.csv'
DrugBank_df = pd.read_csv(DrugBank_triplets_path, sep='\t', header=None)  # (8964, 3)

# 读取STITCH数据
STITCH_triplets_path = base_dir / 'structure' / 'STITCH' / 'STITCH_triplets2.csv'
STITCH_df = pd.read_csv(STITCH_triplets_path, sep='\t', header=None)  # (364853, 3)

# 读取DDinter数据
DDinter_triplets_path = base_dir / 'structure' / 'DDinter' / 'DDinter_triplets.csv'
DDinter_df = pd.read_csv(DDinter_triplets_path, sep='\t', header=None)  # (50765, 3)

# 读取TCMID数据
TCMID_triplets_path = base_dir / 'structure' / 'TCMID' / 'tcmid.csv'
TCMID_df = pd.read_csv(TCMID_triplets_path, sep='\t', header=None)  # (22884, 3)

# 读取FreeText数据
FreeText_path = base_dir / 'non_structure' / 'results'
FreeText_triplets_paths = [p for p in FreeText_path.glob('*triplets.csv') if p.is_file()]
FreeText_df = load_data(FreeText_triplets_paths)  # (87462, 3)

# 合并&去重
nrow = GNBR_df.drop_duplicates(subset=[0, 2]).shape[0]  # 1956235

temp_df = pd.concat([GNBR_df.drop_duplicates(subset=[0, 2]), DrugBank_df, STITCH_df, DDinter_df, TCMID_df, FreeText_df], ignore_index=True)
temp_df.drop_duplicates(subset=[0, 2], keep='first', inplace=True)
temp_df.drop(temp_df.head(nrow).index, inplace=True)
total_triplets_df = pd.concat([GNBR_df, temp_df], ignore_index=True)  # (3395273, 3)
total_triplets_df.to_csv('/data/1011/ZYH/mgkg/data/total_triplets.csv', sep='\t', header=0, index=0)
