#
#   Parse a .jsonlist and report some basic infornmation
#
#   @author Gleb Promokhov
#

import json
from parse_comments import *

# convert .jsonlist to python array
def parse_json(fname):
    lines = open(fname).read().splitlines()
    acc = []
    for l in lines:
        acc.append(json.loads(l))
    return acc

# data = parse_json('CMV_991.jsonlist')
#
# num_comments = 0
# avg_post_len = 0
# avg_comment_len = 0
#
# for s in data:
#     num_comments += count_comments(s['comments'])
#     avg_post_len += len(s['body'])
#     avg_comment_len += avg_comment_length(s['comments'])
#
# avg_post_len = round(avg_post_len/len(data), 2)
# avg_comment_len = round(avg_comment_len/len(data), 2)
#
# print(json.dumps(data[len(data)-1], indent=2))
# print("#POSTS: {}\n#COMMENTS: {}\nAVGPOSTCHARS: {}\nAVGCOMMENTCHARS: {}".format(len(data), num_comments, avg_post_len, avg_comment_len))
