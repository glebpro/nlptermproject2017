#
#   A set of functions useful for getting
#   infornmation from the comment trees.
#
#   @author Gleb Promokhov gleb.promokhov@gmail.com
#

# count number of comments
def count_comments(comments, t=0):
    if comments == []:
        return 0
    for c in comments:
        t += 1 + count_comments(c['children'])
    return t

# get number of deltas awarded
def get_delta_count(comments, t=0):
    if comments == []:
        return 0
    for c in comments:
        if len(c['delta_by_user']) > 0:
            t += 1
        t += get_delta_count(c['children'])
    return t

# get average comment length
def avg_comment_length(comments, cl=0, t=0):
    if comments == []:
        return 0
    for c in comments:
        cl += 1
        t += len(c['body']) + count_comments(c['children'])
    return t/cl
