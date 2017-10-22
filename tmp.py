import praw
import json

creds = json.loads(open('.reddit.auth.json', 'r').read())

reddit = praw.Reddit(client_id=creds["client_id"], client_secret=creds["client_secret"], user_agent=creds["user_agent"])

changemyview = reddit.subreddit('changemyview')

for s in changemyview.new(limit=10):
    print("(^{},{}v) {}".format(s.ups, s.downs, s.title))
    s.comments.replace_more(limit=0)
    for top_level_comment in s.comments:
        print("\t{}".format(top_level_comment.body[:50]+"..."))
