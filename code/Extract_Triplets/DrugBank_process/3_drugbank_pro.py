# 提取三元组
import csv
result = []
with open("/data/1011/ZYH/mgkg/code/DrugBank_process/drug_target.csv", 'r',
          encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    rows = [row for row in reader]
for row in rows:
    print(row)
    result.append(f'{row[1]}\t{row[2]}\t{row[-1]}\n')
with open('/data/1011/ZYH/mgkg/code/DrugBank_process/dt_triple.csv', 'a') as f:
    f.writelines(result)
