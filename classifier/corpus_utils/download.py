import praw
import json
import re
import sys
import time

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
    def deltacomments_h(comments, deltas):
        if comments:
            for c in comments:
                if c['id'] in deltas.keys():
                    c['delta_by_user'] = deltas[str(c['id'])]
                deltacomments_h(c['children'], deltas)

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
        deltacomments_h(coms, comments_with_delta)

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
            author_delta_count = int(author_delta_count.split('∆')[0])
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
    return {
        'id':               submission.fullname,
        'author':           submission.author.name,
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

        if submission.is_self == True \
            and submission.hidden == False \
            and submission.stickied == False:

            sub = parsesubmission(submission)

            # sub['delta'] True if any comments got delta point, False otherwise
            sub['comments'], sub['delta'] = collectcomments(submission, deltalog)
            sub['comment_count'] = countcomments(sub['comments'])

        subs.append(sub)

    return subs

def main():

    # load creds
    creds = json.loads(open('.reddit.auth.json', 'r').read())

    # init reddit
    reddit = praw.Reddit(client_id=creds["client_id"],
                         client_secret=creds["client_secret"],
                         user_agent=creds["user_agent"])
    changemyview = reddit.subreddit('changemyview')
    deltalog = reddit.subreddit('deltalog')

    pull_posts_after = ''
    limit = 100
    _limit = limit
    get_count = 0

    output_file = open('CMV_'+str(_limit)+'.jsonlist', 'w+')

    # pull posts 1 at a time
    while limit != 0:
        limit -= 1
        try:
            submissions = collectsubmissions(changemyview, reddit, pull_posts_after, 1)
            output_file.write(json.dumps(submissions[0], sort_keys=True)+"\n")
            pull_posts_after = submissions[0]['id']
            time.sleep(3)
        except:
            print("Unexpected error:", sys.exc_info()[0])

        print("Curr processing: ", limit)

    output_file.close()

    # for k in submissions[0].keys():
    #     print(k, ' ', submissions[0][k])


    #print(json.dumps(submissions[0], indent=4, sort_keys=True))

if __name__ == "__main__":
    main()
