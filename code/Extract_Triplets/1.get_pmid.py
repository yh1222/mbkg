from Bio import Entrez
import numpy as np

'''分别获取以下四种文献的所有pmid'''
terms = ['microgravity', 'bone loss']
records = []
Entrez.email = '2316444152@qq.com'
for i in range(len(terms)):
    term = terms[i]
    handle1 = Entrez.esearch(db='pubmed', term=term)
    record1 = Entrez.read(handle1)
    count = int(record1['Count'])
    handle2 = Entrez.esearch(db='pubmed', term=term, retmax=count)  # 获取当前term的文献的pmid
    record2 = Entrez.read(handle2)
    records.extend(record2['IdList'])  # 合并四种文献的所有pmid
pmids = np.unique(records)  # 将重复的pmid去除后并从大到小排序
# 将pmid写入txt文件并保存
with open('/data/1011/ZYH/mgkg/data/pmids.txt', 'w+') as f:
    for i in range(len(pmids)):
        pmid = pmids[i]
        f.writelines(f'{pmid}\n')
