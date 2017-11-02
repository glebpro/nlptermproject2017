import json

def parse_json(fname):
    lines = open(fname).read().splitlines()
    acc = []
    for l in lines:
        acc.append(json.loads(l))
    return acc

def count_comments(comments):
    if comments == []:
        return 0
    t = 0
    for c in comments:
        t += 1
        t += count_comments(c['children'])
    return t

def avg_comment_length(comments):
    if comments == []:
        return 0
    t = 0
    for c in comments:
        t += len(c['body'])
        t += count_comments(c['children'])
    return t

data = parse_json('CMV_10000.jsonlist')
cc = 0
avg_cc = 0
avg_post = 0
for s in data:
    cc += count_comments(s['comments'])
    avg_cc += avg_comment_length(s['comments'])
    avg_post += len(s['body'])

avg_cc = round(avg_cc/cc, 2)
avg_post = round(avg_post/len(data), 2)

print(json.dumps(data[len(data)-1], indent=2))
print("#POSTS: {}\n#COMMENTS: {}\nAVGPOSTLENGTH:{}\nAVGCOMMENTLENGTH: {}\n".format(len(data), cc, avg_post, avg_cc))
