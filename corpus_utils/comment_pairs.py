#
#   Find comment threads where there is 1 user with delta and another user
#   in same thread without, and the their Jaccard similarity is close.
#
#   2 comments, similar vocabularies, but what made them different?
#

from corpus_utils.parse_jsonlist import parse_json
from corpus_utils.parse_comments import *

import string
import re
import spacy
from spacy.tokenizer import Tokenizer
import json
import sys

if len(sys.argv) != 2:
    print('usage: python comment_pairs.py CMV_##.jsonlist')
    print()
    quit()
    
def clean(tokens):
    r = []
    for t in tokens:
        t = re.sub('['+string.punctuation+']', '', str(t))
        t = t.lower()
        r.append(t)
    return r

nlp = spacy.load('en_core_web_sm')
tokenizer = Tokenizer(nlp.vocab)

corpus = parse_json(sys.argv[1])

# pairs of comments with Jaccard similarity > MAGIC_DIFF_NUMBER, first delta, second without
#[(comment_with_delta, comment_without_delta_but_similar), ...]
comment_pairs = []

avg_diff_total = 0
total_comments = 0

MAGIC_DIFF_NUMBER = 0.13
avg_diff = 0
count = 0

for s in corpus:

    # skip not useful submissions
    if not len(s['comments']) or not s['delta']:# and s['upvotes'] > 10:
        continue

    op = s['author']

    # find all comments who recived delta from OP
    delta_comments = find_op_delta_comments(s['author'], s['comments'], [])

    for delta_comment in delta_comments:

        # squish comment tree of comments by user who got delta up to comment
        # that got delta, into  one comment
        # delta_squished_comment_tree = squish_comment_tree(delta_comment['author'], s['comments'], delta_comment['id'], '')
        #
        # print("SQUISHED?")
        # print(delta_squished_comment_tree)

        # find another ROOT comment in same submssion that's similar
        # but didn't get delta
        for c in s['comments']:

            if c['author'] != op and c['author'] != delta_comment['author'] and len(c['delta_by_user']) == 0:

                # parse
                delta_comment_clean_set = set(clean(list(tokenizer(delta_comment['body']))))
                nondelta_comment_clean_set = set(clean(list(tokenizer(c['body']))))

                inter = len(delta_comment_clean_set.intersection(nondelta_comment_clean_set))
                un = len(delta_comment_clean_set.union(nondelta_comment_clean_set))

                diff = inter/un

                if diff > MAGIC_DIFF_NUMBER:
                    comment_pairs.append((delta_comment, c))


output = open('comment_pairs.jsonlist', 'w+')

for c in comment_pairs:
    output.write(json.dumps(c)+"\n")

output.close()