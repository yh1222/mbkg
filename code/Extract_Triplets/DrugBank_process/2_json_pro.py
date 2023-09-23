import json

with open('/data/1011/ZYH/mgkg/code/DrugBank_process/drugbank.json', 'r') as f:
    data = json.load(f)
drugs = data['drugbank']['drug']

file = open('/data/1011/ZYH/mgkg/code/DrugBank_process/drug_target.csv', 'w')

for drug in drugs:
    try:
        drug_id = drug['drugbank-id'][0]['#text']
    except Exception:
        drug_id = drug['drugbank-id']['#text']
    drug_name = drug['name']
    try:
        targets = drug['targets']['target']
    except Exception:
        continue
    # print(targets)
    type = drug['@type']

    if isinstance(targets, dict):
        try:
            uniprot_id = targets['polypeptide']['@id']
        except Exception:
            continue
        target_id = targets['id']
        target_name = targets['name']
        item = ','.join([drug_id, drug_name, type, uniprot_id, target_name])
        file.writelines(item+'\n')

    if isinstance(targets, list):

        for target in targets:
            try:
                uniprot_id = target['polypeptide']['@id']
            except Exception:
                continue
            target_id = target['id']
            target_name = target['name']
            item = ','.join(
                [drug_id, drug_name, type, uniprot_id, target_name])
            file.writelines(item+'\n')

file.close()
