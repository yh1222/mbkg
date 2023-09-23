import os
import json
import networkx as nx
from stanfordcorenlp import StanfordCoreNLP
from multiprocessing import Pool
import time


# 导入StanfordCoreNLP的英语语言模型
# pkg_path = 'D:/Model/stanford-corenlp/stanford-corenlp-4.5.1/'
pkg_path = '/data/1011/ZYH/stanford-corenlp/stanford-corenlp-4.5.1/'
nlp = StanfordCoreNLP(pkg_path)


class get_file(object):
    '''同样迭代获取json文件'''
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        files = os.listdir(self.path)
        for file in files:
            file_path = os.path.join(self.path, file)
            yield file_path


def get_dep_triplets(info):
    '''获取句子两两元素及其依存关系的三元组'''
    global nlp
    words = nlp.word_tokenize(info['sentence'])  # 分词
    deps = nlp.dependency_parse(info['sentence'])  # 依存分析
    deps.sort(key=lambda x: x[2])  # 依存结果排序，以便下面获取一一对应的三元组
    head_id = [dep[1] for dep in deps]  # 抽取头实体
    relations = [dep[0] for dep in deps]  # 抽取依存类型
    tail_id = [dep[2] for dep in deps]
    dep_triplets = [(head_id[i], tail_id[i], {'rel': relations[i]}) for i in range(len(words))]
    words.insert(0, 'ROOT')
    return dep_triplets, words


def create_graph(dep_triplets):
    '''根据依存三元组构图'''
    dep_graph = nx.Graph(dep_triplets)
    return dep_graph


def get_entity_pairs(info):
    '''获取五种实体对: g_d, c_d, c_g, g1_g2, g2_g1'''
    g_d, c_d, c_g, g1_g2, g2_g1 = [], [], [], [], []
    genes = [i for i in info['Gene'] if i['identifier'] is not None]
    diseases = [i for i in info['Disease'] if i['identifier'] is not None]
    chemicals = [i for i in info['Chemical'] if i['identifier'] is not None]
    if len(genes) != 0:
        if len(diseases) != 0:
            for gene in genes:
                for disease in diseases:
                    pair = []
                    pair.append(gene)
                    pair.append(disease)
                    g_d.append(pair)
        if len(chemicals) != 0:
            for gene in genes:
                for chemical in chemicals:
                    pair = []
                    pair.append(chemical)
                    pair.append(gene)
                    c_g.append(pair)
        if len(genes) >= 2:
            for g1 in genes:
                for g2 in genes:
                    if g1 == g2:
                        continue
                    pair = []
                    pair.append(g1)
                    pair.append(g2)
                    g1_g2.append(pair)
                    g2_g1.append(pair[::-1])
    if len(chemicals) != 0 and len(diseases) != 0:
        for chemical in chemicals:
            for disease in diseases:
                pair = []
                pair.append(chemical)
                pair.append(disease)
                c_d.append(pair)
    return g_d, c_d, c_g, g1_g2, g2_g1


def get_shortest_path(dep_graph, pairs, words):
    '''获取两个实体之间最短的依存路径'''
    if len(pairs) == 0:
        return []
    shortest_paths = []
    rel = nx.get_edge_attributes(dep_graph, 'rel')
    for pair in pairs:
        if pair[0]['text'] not in words or pair[1]['text'] not in words:  # pubtator中存在的注释错误
            continue
        try:
            nodes = nx.shortest_path(dep_graph, words.index(pair[0]['text']), words.index(pair[1]['text']))  # 依存解析中产生的错误
        except Exception:
            continue
        shortest_path = []
        for i in range(len(nodes) - 1):
            shortest_path.append(words[nodes[i]])
            if (nodes[i], nodes[i+1]) in rel.keys():
                shortest_path.append(rel[(nodes[i], nodes[i+1])])
            else:
                shortest_path.append(rel[(nodes[i+1], nodes[i])])
        # 下面去除了包含'conj'关系的路径
        # 因为这些通常是依存关系解析器表示列表时产生的错误
        if 'conj' in shortest_path or 'nan' in shortest_path:
            continue
        if len(shortest_path) <= 3:
            continue
        try:
            shortest_path[0] = pair[0]
        except IndexError:
            print(shortest_path)
            print(pair)
            print('--------------------')
            continue
        shortest_path.append(pair[1])
        shortest_paths.append(shortest_path)
    return shortest_paths


def create_map(shortest_path):
    '''创建依存路径与实体对的映射'''
    pemap = []
    for path in shortest_path:
        pair = f"{path[0]['text']}\t{path[0]['identifier']}\t{path[-1]['text']}\t{path[-1]['identifier']}"
        dep_path = ""
        for i in path[1:-1]:
            dep_path += f"{i}|"
        dep_path = dep_path.strip('|')
        text = f"{pair}\t{dep_path}\n"
        pemap.append(text)
    return pemap


def func_chain(file_path):
    with open(file_path, 'r') as f:
        content = json.load(f)
    for info in content:
        dep_triplets, words = get_dep_triplets(info)
        dep_graph = create_graph(dep_triplets)
        g_d, c_d, c_g, g1_g2, g2_g1 = get_entity_pairs(info)
        gd_path = get_shortest_path(dep_graph, g_d, words)
        cd_path = get_shortest_path(dep_graph, c_d, words)
        cg_path = get_shortest_path(dep_graph, c_g, words)
        gg_path = get_shortest_path(dep_graph, g1_g2, words) + get_shortest_path(dep_graph, g2_g1, words)
        gd_map = create_map(gd_path)
        cd_map = create_map(cd_path)
        cg_map = create_map(cg_path)
        gg_map = create_map(gg_path)
        if len(gd_map) != 0:
            with open('/data/1011/ZYH/mgkg/data/gene_disease_map.txt', 'a+') as f:
                for line in gd_map:
                    f.writelines(line)
        if len(cd_map) != 0:
            with open('/data/1011/ZYH/mgkg/data/chemical_disease_map.txt', 'a+') as f:
                for line in cd_map:
                    f.writelines(line)
        if len(cg_map) != 0:
            with open('/data/1011/ZYH/mgkg/data/chemical_gene_map.txt', 'a+') as f:
                for line in cg_map:
                    f.writelines(line)
        if len(gg_map) != 0:
            with open('/data/1011/ZYH/mgkg/data/gene_gene_map.txt', 'a+') as f:
                for line in gg_map:
                    f.writelines(line)


def main():
    start = time.time()
    print('开始执行代码(*❦ω❦)，祈祷中……')
    # path = 'D:/Projects/MGKG/mgkg_code/test/annotation_test'
    path = '/data/1011/ZYH/mgkg/data/mature_annotations/'
    file_path = get_file(path)
    with Pool(6) as P:
        P.map(func_chain, file_path)
    end = time.time()
    print(f'执行完毕, sir! func_train耗时{end-start}s.')


if __name__ == '__main__':
    main()
    nlp.close()
