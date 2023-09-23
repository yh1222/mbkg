import math

with open('/data/1011/ZYH/mgkg/data/pmids.txt', 'r') as f:
    content = f.readlines()

# 将pmids.txt文件中的pmid分成四份后分别写入pmid1、pmid2、pmid3、pmid4
start = 0
num = math.ceil(len(content) / 4)
for i in range(1, 5):
    pmids = content[start: start+num]
    with open(f'/data/1011/ZYH/mgkg/data/pmid{i}.txt', 'w+') as f:
        for pmid in pmids:
            f.writelines(pmid)
    start += num
