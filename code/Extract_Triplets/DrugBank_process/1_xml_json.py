import json
import xmltodict

xml = open("/data/1011/ZYH/mgkg/database/DrugBank/full_database.xml").read()
json_file = "/data/1011/ZYH/mgkg/code/DrugBank_process/drugbank.json"
convertJson = xmltodict.parse(xml, encoding='utf-8')
jsonStr = json.dumps(convertJson, indent=1)

with open(json_file, 'w+', encoding='utf-8') as f:
    f.write(jsonStr)
