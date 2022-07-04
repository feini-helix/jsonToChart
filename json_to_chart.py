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
            if action == "Pass":
                line = f"{id}=>operation: {action} | pass"
            else:
                line = f"{id}=>operation: {action} | action"
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

def gen_html(fc_text):
    html_template = '''
<script src="http://cdnjs.cloudflare.com/ajax/libs/raphael/2.3.0/raphael.min.js"></script>
<script src="https://flowchart.js.org/flowchart-latest.js"></script>
<div id="diagram"></div>
<script>
  var chartDef = `REPLACE_ME`;
  var diagram = flowchart.parse(chartDef);
  diagram.drawSVG('diagram');
  // you can also try to pass options:

  diagram.drawSVG('diagram', {
                              'x': 0,
                              'y': 0,
                              'line-width': 3,
                              'line-length': 50,
                              'text-margin': 10,
                              'font-size': 14,
                              'font-color': 'black',
                              'line-color': 'black',
                              'element-color': 'black',
                              'fill': 'white',
                              'yes-text': 'yes',
                              'no-text': 'no',
                              'arrow-end': 'block',
                              'scale': 1,
                              // style symbol types
                              'symbols': {
                                'start': {
                                  'font-color': 'red',
                                  'element-color': 'green',
                                  'fill': 'yellow'
                                },
                                'end':{
                                  'class': 'end-element'
                                }
                              },
                              // even flowstate support ;-)
                              'flowstate' : {
                                'action' : { 'fill' : '#58C4A3', 'font-size' : 12, 'font-color' : 'red', 'font-weight': 'bold'},
                                'pass' : { 'fill' : 'green', 'font-size' : 12, 'font-weight': 'bold'},
                                'future' : { 'fill' : '#FFFF99'},
                              }
                            });
</script>   
'''
    html_txt = html_template.replace("REPLACE_ME", fc_text)
    return html_txt
    
def usage(filename):
    print(f"Usage: python3 {filename} <input_json_file_path> > <output_html_path>")
    
def main(argv):
    if len(argv) == 1 or len(argv) == 2 and argv[1] == "-h":
        usage(argv[0])
    else:
        json_path = argv[1]
        fc_text = gen_flowchart_txt(json_path)
        ret = gen_html(fc_text)
        print(ret)

if __name__ == "__main__":
    main(sys.argv[:])
