from parse_jsonlist import *
import pickle, re, nltk, string
import numpy as np
import os
import sys

file_prefix = os.path.dirname(os.path.realpath(__file__))

"""
this function gathers all of the comments from the comment_pairs file, and
concats each of the comments by author
"""
def gather_comments(comment):

    current = {}
    deltas = {}

    author = comment['author']
    body = comment['body']
    children = comment['children']
    delta = comment['delta_by_user'] != []

    if delta:
        delta = 1
    else:
        delta = 0

    # if the author is already in the dictionary, concat the body
    # otherwise add the author and their delta value
    current[author] = body
    deltas[author] = delta

    if author not in deltas:
        deltas[author] = 0

    # hit the end of a branch, terminating case
    if children == []:
        return current, deltas

    # repeat this process for every child comment
    for child in children:
        # get the body and the delta for the comment
        child_comment, child_delta = gather_comments(child)

        # add the comment and delta to the current dictionary
        for author in child_comment:
            # if the author has already made a comment, append the new comment
            if author in current:
                current[author] += '\n\n' + child_comment[author]
            else:
                current[author] = child_comment[author]

            # if the author got a delta on the way, update that
            if child_delta[author] == 1:
                deltas[author] = 1
            else:
                deltas[author] = 0

    return current, deltas

"""
function to get indices for undersampling
returns list of indices
"""
def undersample(deltas):

    # get the indices of each
    truthy_indices = [i for i in range(len(deltas)) if deltas[i] == 1]
    falsey_indices = [i for i in range(len(deltas)) if deltas[i] == 0]

    # to get a 75/25 split
    max_falsey = len(truthy_indices)

    # pull random falsey indices
    new_falsey = np.random.choice(falsey_indices, max_falsey, replace = False)

    truthy_indices.extend(new_falsey)

    return truthy_indices

"""
assuming input is a list of tokens
returns a converted sentence to negate polarity
"""
def convert_sent(sent):
    # print(len(sent))
    for i in range(len(sent)):
        tok = sent[i]
        if re.search("not\\b", tok) or re.search("n't", tok):
            if i < len(sent) - 1:
                j = i + 1
                nexttok = sent[j]
                flag = True
                while nexttok not in string.punctuation:
                    sent[j] = "not_" + nexttok
                    j += 1
                    if j == len(sent):
                        break
                    nexttok = sent[j]
    return sent

"""
function to load bing lexicon
returns two lists, first positive list then negative list
"""
def get_lexicons():
    pos = open(file_prefix+"/positive-words.txt")
    neg = open(file_prefix+"/negative-words.txt")

    pos_list = [line.strip() for line in pos.readlines()]
    neg_list = [line.strip() for line in neg.readlines()]

    return pos_list, neg_list

"""
assuming the input is a comment
outputs a tuple of #pos words and #neg words
"""
def count_sentiment(sent, pos, neg):
    sent = convert_sent(nltk.word_tokenize(sent))
    pos_count = 0
    neg_count = 0
    for tok in sent:
        if re.sub("(not_)?(.*)", "\\2", tok) in pos:
            if re.match("not_", tok):
                neg_count += 1
            else:
                pos_count += 1
        elif re.sub("(not_)?(.*)", "\\2", tok) in neg:
            if re.match("not_", tok):
                pos_count += 1
            else:
                neg_count += 1
    return pos_count, neg_count

"""
count the proportion of links in a comment
returns tuple of edu, com, pdf
"""
def count_links(sent):

    edu_count = len(re.findall("\.edu", sent))
    com_count = len(re.findall("\.com", sent))
    pdf_count = len(re.findall("\.pdf", sent))

    total_links = sum((edu_count, com_count, pdf_count))

    if total_links > 0:
        return edu_count / total_links, com_count / total_links, pdf_count / total_links

    return edu_count, com_count, pdf_count

"""
count occurrences of markdown in a sentence
"""
def count_md(sent):

    num_italic = len(re.findall("_.*?_", sent))
    num_bold = len(re.findall("\*\*.*?\*\*", sent))
    num_block = len(re.findall(">", sent))

    return num_italic, num_bold, num_block

"""
long annoying function to get list of POS tags
"""
def get_init_list():
    init_list = {
        "CC": 0,
        "CD": 0,
        "DT": 0,
        "EX": 0,
        "FW": 0,
        "IN": 0,
        "JJ": 0,
        "JJR": 0,
        "JJS": 0,
        "LS": 0,
        "MD": 0,
        "NN": 0,
        "NNS": 0,
        "NNP": 0,
        "NNPS": 0,
        "PDT": 0,
        "POS": 0,
        "PRP": 0,
        "PRP": 0,
        "PRP$": 0,
        "RB": 0,
        "RBR": 0,
        "RBS": 0,
        "RP": 0,
        "TO": 0,
        "UH": 0,
        "VB": 0,
        "VBD": 0,
        "VBG": 0,
        "VBN": 0,
        "VBP": 0,
        "VBZ": 0,
        "WDT": 0,
        "WP": 0,
        "WP$": 0,
        "WRB": 0
    }

    return init_list

"""
get proportion of POS tags in a comment
"""
def count_pos(sent):
    sent = nltk.word_tokenize(sent)
    init_list = get_init_list()

    total_len = len(sent)

    for k, v in nltk.pos_tag(sent):
        if v in init_list:
            init_list[v] += 1

    outlist = []
    for k in init_list:
        if total_len > 0:
            outlist.append(init_list[k] / total_len)
        else:
            outlist.append(init_list[k])

    return outlist

def usage():
    print("usage: python get_features.py path/to/comment_pairs.jsonlist")
    print()
    quit()

def main():

    if len(sys.argv) != 2:
        usage()

    # gather 22735 pairs
    data = parse_json(sys.argv[1])

    comments = []
    deltas = []

    for pair in data:
        for comment in pair:
            current_comment, current_delta = gather_comments(comment)
            for author in current_comment:
                comments.append(current_comment[author])
                deltas.append(current_delta[author])

    # since there are somehow still dupes...
    final_comments = []
    final_deltas = []
    for i in range(len(comments)):
        if (comments[i] != '[removed]') and (comments[i] not in final_comments):
            final_comments.append(comments[i])
            final_deltas.append(deltas[i])

    # let's save these for later
    pickle.dump(final_comments, open(file_prefix+"/full_comments2.sav", "wb"))
    pickle.dump(final_deltas, open(file_prefix+"/full_y2.sav", "wb"))

    undersampled_comments = []
    undersampled_deltas = []
    # now for the undersampling
    undersampled_indices = undersample(final_deltas)
    for i in range(len(final_comments)):
        if i in undersampled_indices:
            undersampled_comments.append(final_comments[i])
            undersampled_deltas.append(final_deltas[i])

    # let's save these as well
    pickle.dump(undersampled_comments, open(file_prefix+"/undersampled_comments2.sav", "wb"))
    pickle.dump(undersampled_deltas, open(file_prefix+"/undersampled_deltas2.sav", "wb"))

    # now it's time to extract all of the features.
    # first we need to load the Bing lexicons
    pos, neg = get_lexicons()
    pos_counts = [count_pos(comm) for comm in undersampled_comments]
    sentiments = [count_sentiment(comm, pos, neg) for comm in undersampled_comments]
    md_counts = [count_md(comm) for comm in undersampled_comments]
    link_counts = [count_links(comm) for comm in undersampled_comments]

    # now glue all of these together for the final X matrix
    for i in range(len(pos_counts)):
        pos_counts[i].extend(sentiments[i])
        pos_counts[i].extend(md_counts[i])
        pos_counts[i].extend(link_counts[i])

    # now save it to be ready for the modelling
    pickle.dump(pos_counts, open(file_prefix+"/undersampled_X2.sav", "wb"))

if __name__ == "__main__":
    main()
