import pandas as pd
import numpy as np
from glob import iglob


class load_data(object):
    def __init__(self, dir_path):
        self.file_path = dir_path + '*_map.txt'

    def __iter__(self):
        for file in iglob(self.file_path):
            print(file)
            df = pd.read_table(file, delimiter='\t', header=None)
            df.columns = ['head_name', 'head_id', 'tail_name', 'tail_id', 'dependency_path']
            yield df, file


def preparation(df):
    entity_pairs = []
    dependency_paths = []
    for _, row in df.iterrows():
        entity_pair = str(row['head_id']) + '|' + str(row['tail_id'])
        if entity_pair not in entity_pairs:
            entity_pairs.append(entity_pair)
        if row['dependency_path'] not in dependency_paths:
            dependency_paths.append(row['dependency_path'])
    return entity_pairs, dependency_paths


def clean_dp(matrix):
    matrix.loc['Col_sum'] = matrix.apply(lambda x: x.sum(), axis=0)
    i = 0
    drop_column = []
    for dp_num in matrix.loc['Col_sum', ]:
        if dp_num == 1:
            drop_column.append(i)
        i += 1
    matrix.drop(matrix.columns[drop_column], axis=1, inplace=True)
    matrix.drop('Col_sum', axis=0, inplace=True)


def clean_entity(matrix, entity_pairs):
    matrix['Row_sum'] = matrix.apply(lambda x: x.sum(), axis=1)
    i = 0
    drop_row = []
    for entity_num in matrix.loc[:, 'Row_sum']:
        if entity_num == 0:
            drop_row.append(i)
        i += 1
    matrix.insert(loc=0, column='entity_pair', value=entity_pairs)
    matrix.drop(matrix.index[drop_row], axis=0, inplace=True)
    matrix.drop('Row_sum', axis=1, inplace=True)


def create_matrix(df, entity_pairs, dependency_paths):
    empty_matrix = np.zeros(shape=(len(entity_pairs), len(dependency_paths)))
    matrix = pd.DataFrame(empty_matrix, columns=dependency_paths)
    for _, row in df.iterrows():
        index = entity_pairs.index(str(row['head_id']) + '|' + str(row['tail_id']))
        dp = row['dependency_path']
        matrix.loc[index, dp] = 1
    # 删除只连接一对实体的依存路径和只被一条依存路径连接的实体对
    clean_dp(matrix)
    clean_entity(matrix, entity_pairs)
    return matrix


def save_matrix(matrix, save_path):
    matrix_name = save_path.split('/')[-1]
    print(f'生成矩阵: {matrix_name}')
    matrix.to_csv(save_path, sep='\t', index=False)


def run(info):
    save_path = '/data/1011/ZYH/mgkg/data/' + info[1].split('/')[-1].split('.')[0] + '_matrix.csv'
    df = info[0]
    entity_pairs, dependency_paths = preparation(df)
    matrix = create_matrix(df, entity_pairs, dependency_paths)
    save_matrix(matrix, save_path)
    print('生成完毕')


def main():
    dir_path = '/data/1011/ZYH/mgkg/data/'
    info = load_data(dir_path)
    list(map(run, info))


if __name__ == '__main__':
    main()
