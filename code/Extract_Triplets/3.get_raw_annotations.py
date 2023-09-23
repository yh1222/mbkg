import requests
import json
from multiprocessing import Pool
import sys


class load_pmids(object):
    '''爬取的数据量较大, 使用迭代器生成文件路径'''
    def __init__(self, file_path):
        self.file = file_path

    def __iter__(self):
        with open(self.file, 'r') as f:
            for line in f:
                yield line.strip()


def get_url(pmid):
    '''根据pmid生成url'''
    url = f'https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmids={pmid}'
    return url


def get_raw_annotations(url):
    '''从pubtator上获取原注释'''
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29"}
    s = requests.session()
    requests.adapters.DEFAULT_RETRIES = 9  # 增加重连次数
    response = s.get(url, headers=header).text.strip()
    raw_annotations = json.loads(response)
    return raw_annotations


def func_chain(pmid):
    '''设置log文件, 用于断点续爬, log中已含有的pmid'''
    num = sys.argv[1]
    record_path = f'/data/1011/ZYH/mgkg/data/pmids_record{num}.txt'
    with open(record_path, 'a+') as f:
        f.seek(0)
        for i in f:
            line = i.strip()
            if line == str(pmid):
                return 0
        else:
            url = get_url(pmid)
            # 因为有些文献在pubtator上的注释内容为空，所以会导致json解析失败
            # 因此将这些空文献跳过
            try:
                raw_annotations = get_raw_annotations(url)
                save_path = f'/data/1011/ZYH/mgkg/data/raw_annotations/{pmid}.json'
                with open(save_path, 'w+') as fo:
                    json.dump(raw_annotations, fo)
                f.write(f'{pmid}\n')
            except json.decoder.JSONDecodeError:
                print(f'error: {pmid}')


def main():
    num = sys.argv[1]
    file_path = f'/data/1011/ZYH/mgkg/data/pmid{num}.txt'
    pmids = load_pmids(file_path)
    with Pool(4) as P:
        P.map(func_chain, pmids)


if __name__ == '__main__':
    main()
