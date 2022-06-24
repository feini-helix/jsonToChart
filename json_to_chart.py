import sys
import json

def get_condition(rule):
    condition = ""
    if "details" not in rule and "action" in rule["details"]:
        raise Exception("invalid condition rule: {}".format(rule))
    details = rule["details"]
    if "requeueType" in details:
        id = rule["id"]
        operator = details["operator"]
        threshold = details["threshold"]
        condition = f"{id} {operator} {threshold}"
    elif "value" in details:
        metric = details["metric"]
        valule = details["value"]
        condition = f"{metric} == {valule}"
    elif len(details.keys()) == 2 and "operator" in details and "threshold" in details:
        category = rule["category"]
        operator = details["operator"]
        threshold = details["threshold"]
        condition = f"{category} {operator} {threshold}"
    elif "operator" in details and "threshold" in details and "metric" in details:
        metric = details["metric"]
        operator = details["operator"]
        threshold = details["threshold"]
        condition = f"{metric} {operator} {threshold}"
    return condition

def create_flowchart(items):
    lines = []
    line = ""
    lines.append("st=>start")
    lines.append("e=>end")
    lines.append("")
    for item in items:
        if item["type"] == "condition":
            id = item["id"]
            condition = item["condition"]
            line = f"{id}=>condition: {condition}"
            lines.append(line)
        elif item["type"] == "action":
            id = item["id"]
            action = item["action"]
            line = f"{id}=>operation: {action}"
            lines.append(line)
    lines.append("")
    first_item_id = items[0]["id"]
    lines.append(f"st->{first_item_id}")
    for item in items:
        if item["type"] == "condition":
            id = item["id"]
            p = item["pass"]
            f = item["fail"]
            lines.append(f"{id}(yes)->{p}")
            lines.append(f"{id}(no)->{f}")
        elif item["type"] == "action":
            pass
    return "\n".join(lines)
    
def gen_flowchart_txt(jsonPath):
    content = {}
    items = []
    with open(jsonPath) as fp:
        content = json.loads(fp.read())
    rules = content["rules"]
    for rule in rules:
        item = {}
        item["id"] = rule["id"]
        item["category"] = rule["category"]
        if "action" in rule["details"]:
            item["type"] = "action"
            item["action"] = rule["details"]["action"]
        else:
            item["type"] = "condition"
            item["pass"] = rule["pass"]
            item["fail"] = rule["fail"]            
            item["condition"] = get_condition(rule)
        items.append(item)
    content = create_flowchart(items)
    return content

def usage(filename):
    print(f"Usage: python3 {filename} <input_json_file_path> > <output_flowchart_file_path>")
    
def main(argv):
    if len(argv) == 1 or len(argv) == 2 and argv[1] == "-h":
        usage(argv[0])
    else:
        json_path = argv[1]
        ret = gen_flowchart_txt(json_path)
        print(ret)

if __name__ == "__main__":
    main(sys.argv[:])
