import pandas as pd
import glob


def get_file_path():
    part1_paths = glob.glob(r'/data/1011/ZYH/mgkg/database/GNBR/part-i-*.txt')
    part2_paths = glob.glob(r'/data/1011/ZYH/mgkg/database/GNBR/part-ii-*-with-themes.txt')
    part1_paths = sorted(part1_paths)
    part2_paths = sorted(part2_paths)
    return part1_paths, part2_paths


def read_part_i(file_path):
    '''读取part-i文件, 并提取出依存路径对应的theme'''
    theme = pd.read_table(file_path, sep='\t', header=None, nrows=1)
    ncols = theme.shape[1]
    selected_cols = [0] + [i for i in range(1, ncols, 2)]
    theme = pd.read_table(file_path, sep='\t', header=0, usecols=selected_cols)
    theme['theme'] = theme.iloc[:, 1:].idxmax(axis=1)
    theme = theme.loc[:, ['path', 'theme']]
    return theme


def read_part_ii(file_path):
    '''读取part-ii文件, 并提取出实体对(id)及其对应的依存路径'''
    dp = pd.read_table(file_path, sep='\t', header=None, usecols=[8, 9, 12])
    dp.dropna(axis=0, how='any', inplace=True)
    dp.columns = ['start_entity', 'end_entity', 'path']
    return dp


def match_dp_theme(theme, dp):
    '''匹配依存路径和theme, 注意part-i和ii中的start_entity和end_entity的大小写不一样, 因此比对时需要忽略大小写'''
    theme['path'] = theme['path'].str.lower()
    dp['path'] = dp['path'].str.lower()
    match_df = pd.merge(dp, theme, on='path')
    return match_df


def extract_triplets(match_df, save_path):
    '''提取三元组(h, r, t)并保存为csv文件, 分隔符为制表符, 不保留行索引和列名'''
    match_df.drop(columns='path', axis=1, inplace=True)
    match_df = match_df[['start_entity', 'theme', 'end_entity']]  # 调换顺序, 变为(h, r, t)
    match_df.to_csv(save_path, sep='\t', index=0, header=0)


def main():
    part1_paths, part2_paths = get_file_path()
    for i in range(4):
        part1 = part1_paths[i]
        part2 = part2_paths[i]
        print(f'Batch-{i}')
        print(f'part-i file: {part1}')
        print(f'part-ii file: {part2}')
        names = part1.split('/')[-1].split('-')
        save_path = '/data/1011/ZYH/mgkg/data/structure/' + names[2] + '_' + names[3] + '_triplets.csv'
        print(f'save path is {save_path}')
        theme = read_part_i(part1)
        dp = read_part_ii(part2)
        match_df = match_dp_theme(theme, dp)
        extract_triplets(match_df, save_path)
        print(f'---------Batch-{i} over---------')


if __name__ == '__main__':
    main()
