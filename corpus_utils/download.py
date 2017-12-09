#
#   Download posts from /r/changemyview as a JSON object.
#   Each JSON post object written as 1 line to output file
#   See data_format_readme.txt for how JSON object works.
#
#   Some varialbes such as number of posts to collect
#   can be adjusted in main().
#
#   TODO: this script is horrible and very specific to
#   what I needed for the term project. Will generalize
#   when I have the time
#
#   @author Gleb Promokhov gleb.promokhov@gmail.com
#


import praw
import prawcore as prawcore
import json
import re
import sys
import os
import time
import logging
import requests

# recursivley count comments
def countcomments(comments, acc=0):
    if len(comments) == 0:
        return 0
    else:
        acc += len(comments)
        for c in comments:
            acc += countcomments(c['children'])
        return acc

# gather comments of particualr submission into tree-like strucutre
# reutrns: [top_level_comments], each comment has 'children' attribute that
# lists next level of comments
# returns: True if any comments got delta, False otherwise
def collectcomments(submission, reddit):

    # recursivley collect comment tree
    def collectcomments_h(replies):
        if len(replies) == 0:
            return []
        else:
            reps = []
            for r in replies:
                r_tmp = parsecomment(r)
                if r_tmp['author'] != 'DeltaBot':
                    r_tmp['children'] = collectcomments_h(r.replies)
                    reps.append(r_tmp)
            return reps

    # apply deltapoints to relevent comments
    def deltacomments_h(comments, parent, deltas):
        if comments:
            for c in comments:
                if c['id'] in deltas.keys():
                    parent['delta_by_user'] = deltas[str(c['id'])]
                deltacomments_h(c['children'], c, deltas)

    coms = []
    delta = False

    # expand all 'More Comments -->' links
    submission.comments.replace_more(limit=0)

    # parse comments
    deltabots_comment = ''
    for top_level_comment in submission.comments:
        com = parsecomment(top_level_comment)
        if com['author'] == 'DeltaBot':
            deltabots_comment = com
        else:
            com['children'] = collectcomments_h(top_level_comment.replies)
            coms.append(com)

    # if DeltaBot worked, return { comment_fullname:[users_who_awarded_point, ...], ... }
    if deltabots_comment != '':
        delta = True
        comments_with_delta = collectdeltas(deltabots_comment, reddit)
        # which user(s) awarded delta points to which comment
        deltacomments_h(coms, '', comments_with_delta)

    return coms, delta

# collect which users awarded
def collectdeltas(deltabots_comment, reddit):

    # get submission id in /r/deltalog
    log_id = re.search('/r/DeltaLog/comments/(.+?)\)', deltabots_comment['body']).group(1)
    submission = praw.models.Submission(reddit, id=log_id)

    # how to regex LOL
    submission = submission.selftext.split('DB3PARAMSSTART')[1].strip().split('DB3PARAMSEND')[0].strip()
    submission = json.loads(submission)
    output = {}

    for c in submission['comments']:
        if c['deltaCommentFullName'] not in output.keys():
            output[c['deltaCommentFullName']] = []
            # output[c['deltaCommentFullName']].append(c['awardingUsername'])
            output[c['deltaCommentFullName']].append(c['awardingUsername'])

        else:
            output[c['deltaCommentFullName']].append(c['awardingUsername'])

    return output

# return dict with only certain comment data
def parsecomment(comment, ignore=0):

    author = comment.author
    if author == None:
        author = 'DELETED'
    else:
        author = author.name

    author_delta_count = comment.author_flair_text
    if author_delta_count == None:
        author_delta_count = 0
    else:
        if '∞' not in author_delta_count:

            # I cannot figure why this breaks when author_delta_count = '1∆'
            try:
                author_delta_count = int(author_delta_count.replace('∆', ''))
            except ValueError:
                author_delta_count = 1
        else:
            author_delta_count = 0

    return {
        'archived':             comment.archived,
        'author':               author,
        'author_delta_count':   author_delta_count,
        'body':                 comment.body,
        'created_utc':          comment.created_utc,
        'downvotes':            comment.downs,
        'edited':               comment.edited,
        'id':                   comment.fullname,
        'gilded':               comment.gilded,
        'num_reports':          comment.num_reports,
        'permalink':            comment.permalink,
        'score_hidden':         comment.score_hidden,
        'stickied':             comment.stickied,
        'upvotes':              comment.ups,
        'user_reports':         comment.user_reports,
        'children':             [],
        'delta_by_user':        [],
    }

# return dict with only certain submission data
def parsesubmission(submission):


    author = ''
    if submission.author == None:
        author = 'DELETED'
    else:
        author = submission.author.name

    return {
        'id':               submission.fullname,
        'author':           author,
        'title':            submission.title,
        'created_utc':      submission.created_utc,
        'upvotes':          submission.ups,
        'downvotes':        submission.downs,
        'edited':           submission.edited,
        'locked':           submission.locked,
        'num_reports':      submission.num_reports,
        'permalink':        submission.permalink,
        'body':             submission.selftext_html,
        'comments':         [],
        'delta':            False,
        'archived':         submission.archived,
    }

# gather posts and comments
def collectsubmissions(changemyview, deltalog, pull_posts_after, limit):

    unparsedsubs = []
    subs = []

    if pull_posts_after == '':
        unparsedsubs = changemyview.new(limit=limit)
    else:
        unparsedsubs = changemyview.new(limit=limit, params={ 'after': pull_posts_after })

    for submission in unparsedsubs:

        sub = {} # parsed submission
        pull_posts_after = submission.fullname

        if submission.is_self == True \
            and submission.hidden == False \
            and submission.stickied == False \
            and submission.author != 'Snorrrlax': # ignore mod

            print('Parsing: ', submission)
            sub = parsesubmission(submission)

            # sub['delta'] True if any comments got delta point, False otherwise
            sub['comments'], sub['delta'] = collectcomments(submission, deltalog)
            sub['comment_count'] = countcomments(sub['comments'])

            subs.append(sub)

    if len(subs) == 0:
        return [], pull_posts_after

    return subs, subs[len(subs)-1]['id']

def usage():
    print('$ python download.py number_posts_to_collect')
    print()
    quit()

def main():

    # class JSONDebugRequestor(prawcore.Requestor):
    #     def request(self, *args, **kwargs):
    #         response = super().request(*args, **kwargs)
    #         print(json.dumps(response.json(), indent=4))
    #         return response

    if len(sys.argv) != 2:
        usage()

    # load creds
    creds = json.loads(open(os.path.dirname(os.path.realpath(__file__))+'/reddit.auth.json', 'r').read())

    # init reddit
    my_session = requests.Session()
    reddit = praw.Reddit(client_id=creds["client_id"],
                         client_secret=creds["client_secret"],
                         user_agent=creds["user_agent"],
                         # requestor_class=JSONDebugRequestor,
                         requestor_kwargs={'session': my_session})
    changemyview = reddit.subreddit('changemyview')
    deltalog = reddit.subreddit('deltalog')

    # init logger
    # handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    # logger = logging.getLogger('prawcore')
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(handler)


    pull_posts_after = ''
    limit = int(sys.argv[1])
    _limit = limit
    get_count = 1

    output_file = open('CMV_'+str(_limit)+'.jsonlist', 'a')
    print("^c to safely quit")

    while limit > 0:
        limit -= get_count
        try:
            submissions, next_post = collectsubmissions(changemyview, reddit, pull_posts_after, get_count)
            pull_posts_after = next_post
            if len(submissions) > 0:
                for s in submissions:
                    output_file.write(json.dumps(s, sort_keys=True)+"\n")
            time.sleep(3)
        except:
            the_type, the_value, the_traceback = sys.exc_info()
            if the_type == KeyboardInterrupt:
                quit()
            print(the_type)
            print(the_traceback)
            print(the_value)
            raise the_type

        print("Curr processing: ", limit)

    output_file.close()

    # for k in submissions[0].keys():
    #     print(k, ' ', submissions[0][k])


    #print(json.dumps(submissions[0], indent=4, sort_keys=True))

if __name__ == "__main__":
    main()
