import os
import json
from multiprocessing import Pool
from nltk.tokenize import sent_tokenize
import re


class get_file(object):
    '''迭代输出json文件, 节省内存'''
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        dirs = os.listdir(self.path)
        for file in dirs:
            file_path = os.path.join(self.path, file)
            yield file_path


# 加载json文件中的内容并获取该文件对应的pmid
def get_raw_ann(file_path):
    with open(file_path, 'r') as f:
        ann_raw = json.load(f)
    df = file_path.split('/')[-1]
    pmid = df.split('.')[0]
    return ann_raw, pmid


# 获取我们需要的注释类型，保存为字典格式
def ann_filter(ann_raw, pmid, entity_type):
    ann_dict = {}
    ann_dict['id'] = pmid
    ann_dict['passages'] = []
    for i in ann_raw['passages']:
        ann_dict['passages'].append({'text': i['text'], 'annotations': [x for x in i['annotations'] if x['infons']['type'] in entity_type and x['infons']['identifier'] != '-']})
    return ann_dict


# 将注释对应的文本分成句子
def sent_split(ann_dict):
    title = ann_dict['passages'][0]['text']
    abstract = ann_dict['passages'][1]['text']
    sentences = [title + ' '] + [i + ' ' for i in sent_tokenize(abstract)]
    annotation = ann_dict['passages'][0]['annotations'] + ann_dict['passages'][1]['annotations']
    sent_len = [len(i) for i in sentences]
    return sentences, sent_len, annotation


# 将句子与注释进行匹配
def sent_match(sent_len, annotation):
    for index in range(len(annotation)):
        sent_loc = annotation[index]['locations'][0]['offset']
        entity_len = annotation[index]['locations'][0]['length']
        sent_num = 0
        for i in sent_len:
            if sent_loc > i:
                sent_loc -= i
                sent_num += 1
            else:
                break
        # 将offset改成注释在每句话中的位置
        annotation[index]['location'] = {'sent_num': sent_num, 'offset': sent_loc, 'length': entity_len}
        del annotation[index]['locations']
    return annotation


# 筛选含有两个及以上注释的句子
def sent_filter(sentences, annotation, pmid):
    sent_del = []
    for i in range(len(sentences)):
        sent_ann = [j for j in annotation if j['location']['sent_num'] == i]
        # 只选取有多个注释的句子
        if len(sent_ann) < 2:
            sent_del.append(i)
            annotation = [i for i in annotation if i not in sent_ann]  # 剔除只含一个注释的句子
        else:  # 含两个注释的句子不一定都是有用的
            entity_type = [i['infons']['type'] for i in sent_ann]
            dis_num = entity_type.count('Disease')
            che_num = entity_type.count('Chemical')
            gen_num = entity_type.count('Gene')
            if gen_num >= 2:
                pass
            elif che_num >= 1 and dis_num >= 1:
                pass
            elif che_num >= 1 and gen_num >= 1:
                pass
            elif gen_num >= 1 and dis_num >= 1:
                pass
            else:
                sent_del.append(i)
                annotation = [i for i in annotation if i not in sent_ann]
    # 报错位置，跳过出错文件，并输出错误文件的PMID
    try:
        filter_sentences = [i for i in sentences if sentences.index(i) not in sent_del]
        for i in annotation:
            i['location']['sent_num'] = filter_sentences.index(sentences[i['location']['sent_num']])
    except IndexError:
        print(f'IndexError pmid is {pmid}')
    except ValueError:
        print(f'ValueError pmid is {pmid}')
    return filter_sentences, annotation


def entity_atom(sentences, annotation, pmid):
    for ann in annotation:
        if re.search(r"\s|-", ann['text']):
            try:
                ann['text'] = re.sub(r"\s|-", "_", ann['text'])
                new_sentence = sentences[ann['location']['sent_num']][:ann['location']['offset']]+ann['text']+sentences[ann['location']['sent_num']][ann['location']['offset']+ann['location']['length']:]
                sentences[ann['location']['sent_num']] = new_sentence
            except IndexError:  # 错误文件很少，记录错误pmid，手动纠错更快
                print(f'{pmid} in error during entity_atom')
    return annotation, sentences


# 保存到本地
def output(sentences, annotation, pmid):
    save_path = f'/data/1011/ZYH/mgkg/data/mature_annotations/{pmid}.json'
    result = []
    for index in range(len(sentences)):
        sent_dict = {'sentence': sentences[index], 'Gene': [], 'Disease': [], 'Chemical': []}
        sent_ann = [i for i in annotation if i['location']['sent_num'] == index]
        for i in sent_ann:
            sent_dict[i['infons']['type']].append({'text': i['text'], 'identifier': i['infons']['identifier']})
        result.append(sent_dict)
    with open(save_path, 'w+') as f:
        json.dump(result, f)


def func_chain(file_path):
    entity_type = ['Gene', 'Disease', 'Chemical']
    ann_raw, pmid = get_raw_ann(file_path)
    with open('/data/1011/ZYH/mgkg/data/annot_record.txt', 'a+') as fo:
        fo.seek(0)
        for i in fo:
            line = i.strip()
            if line == str(pmid):
                return 0
        try:
            ann_dict = ann_filter(ann_raw, pmid, entity_type)
        except KeyError:
            print(f'KeyError pmid is {pmid}')
            return 0
        sentences, sent_end, annotation = sent_split(ann_dict)
        annotation = sent_match(sent_end, annotation)
        sentences, annotation = sent_filter(sentences, annotation, pmid)
        if len(sentences) > 0:
            annotation, sentences = entity_atom(sentences, annotation, pmid)
            output(sentences, annotation, pmid)
            fo.write(f'{pmid}\n')


def main():
    path = '/data/1011/ZYH/mgkg/data/raw_annotations/'
    file_path = get_file(path)
    with Pool(6) as P:
        P.map(func_chain, file_path)


if __name__ == '__main__':
    main()
