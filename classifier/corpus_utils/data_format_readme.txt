
CMV_##.jsonlist are submissions to /r/ChangeMyView, 1 submission per line as a
JSON object.

Each submission has the following data:

SUBMISSION:
    'id':               't3_######'
    'author':           username of author
    'title':            title
    'created_utc':      when submission created in UTC
    'upvotes':          upvotes
    'downvotes':        downvotes
    'edited':           true/false if submission edited
    'locked':           true/false if submission locked
    'num_reports':      number of times this post as reported
    'permalink':        permalink
    'body':             html of body text
    'comments':         list of comments
    'delta':            if any deltas were awarded in comments
    'archived':         true/false if submission archived

Comments are recorded as tree-like structures, a list of comment JSON objects,
each comment has a 'children' field that is another list of comments

COMMENT:
    'archived':             true/false if comment archived
    'author':               username of author
    'author_delta_count':   how many delta points author has
    'body':                 html of body
    'created_utc':          when comment created in utc
    'downvotes':            upvotes
    'edited':               true/false if comment edited
    'id':                   't1_######'
    'gilded':               if comment was gilded
    'num_reports':          number of times this comment was reported
    'permalink':            permalink to comment
    'score_hidden':         if comment score is hidden
    'stickied':             true/false if comment sticked
    'upvotes':              upvotes
    'user_reports':         usernames of people who reported comment
    'children':             list of comments that replied to this one
    'delta_by_user':        usernames of people who awareded delta to comment
