import xml.etree.ElementTree as ET
import numpy as np


def mesh_parse(tree, dic, target_ui, target_name):
    root = tree.getroot()
    for ui, name in zip(root.iter(target_ui), root.iter(target_name)):
        string = name.find('String').text
        if string not in dic:
            dic[string] = ui.text


def main():
    tree = ET.ElementTree()
    mesh = {}
    files = ["/data/1011/ZYH/mgkg/database/MESH/desc2023.xml", "/data/1011/ZYH/mgkg/database/MESH/pa2023.xml", "/data/1011/ZYH/mgkg/database/MESH/supp2023.xml"]
    target_ui = ['DescriptorUI', 'RecordUI', 'SupplementalRecordUI']
    target_name = ['DescriptorName', 'RecordName', 'SupplementalRecordName']
    for i in range(len(files)):
        file = files[i]
        tree.parse(file)
        mesh_parse(tree, mesh, target_ui[i], target_name[i])
    np.save('/data/1011/ZYH/mgkg/database/MESH/items_dict.npy', mesh)


if __name__ == '__main__':
    main()
