import json
import sys

import random
import string

# 从所有字母和数字中生成随机字符串
def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

# 读取每个panel中的 target
# 将 target 的 legend 命名为 namespace + subsystem + title + [name]
def read_targets(file_name, target_id_len = 5):
    with open(file_name, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return read_targets_from_json(data, target_id_len)

def read_targets_from_json(data, target_id_len = 5):
    targets = []
    current_namespace = data["title"]
    current_subsystem = ""

    for panel in data["panels"]:
        if panel["type"] == "row":
            # do row
            current_subsystem = panel["title"]
           
        elif panel["type"] == "timeseries":
            # do timeseries
            current_name = panel["title"]
            
            for target in panel["targets"]:
                target["refId"] = generate_random_string(target_id_len)

                legend = [current_namespace, current_subsystem, current_name]
                if target["legendFormat"] != "__auto":
                    legend.append(target["legendFormat"])
                    
                legend = ' '.join(legend).replace(' ', '_').lower()
                target["legendFormat"] = legend

                targets.append(target)
    return targets   


