from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import os


def read_matrix(read_path):
    matrix = pd.read_csv(read_path, sep='\t')
    return matrix


def km_cluster(cnum, matrix):
    dp_matrix = matrix.iloc[:, 1:]
    kmeans = KMeans(n_clusters=cnum)
    kmeans.fit(np.array(dp_matrix))
    cluster_result = kmeans.predict(np.array(dp_matrix))
    return cluster_result


def pair_cluster(matrix, cluster_result):
    pair = matrix.iloc[:, 0]
    cluster = pd.DataFrame(cluster_result, columns=['cluster'])
    final_result = pd.concat([pair, cluster], axis='columns')
    return final_result


def output_cluster(save_path, final_result):
    final_result.to_csv(save_path, sep='\t', index=False)


def main():
    cnum = [7, 10, 10, 9]
    matrix_name = ['chemical_disease_map_matrix.csv', 'chemical_gene_map_matrix.csv', 'gene_disease_map_matrix.csv', 'gene_gene_map_matrix.csv']
    save_name = ['chemical_disease_cluster.csv', 'chemical_gene_cluster.csv', 'gene_disease_cluster.csv', 'gene_gene_cluster.csv']
    dir_path = '/data/1011/ZYH/mgkg/data/'
    for i in range(4):
        read_path = os.path.join(dir_path, matrix_name[i])
        save_path = os.path.join(dir_path, save_name[i])
        print(f'读取文件: {read_path}')
        matrix = read_matrix(read_path)
        print('开始聚类')
        cluster_result = km_cluster(cnum[i], matrix)
        final_result = pair_cluster(matrix, cluster_result)
        print(f'储存结果: {save_path}')
        output_cluster(save_path, final_result)
        print('储存完毕')


if __name__ == '__main__':
    main()
