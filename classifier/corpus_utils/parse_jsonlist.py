import json

def parse_json(fname):
    lines = open(fname).read().splitlines()
    acc = []
    for l in lines:
        acc.append(json.loads(l))
    return acc

# data = parse_json('CMV_5.jsonlist')
# for l in data:
#     print(json.dumps(l, indent=2))
#
# print(len(data))
