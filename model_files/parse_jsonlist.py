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
