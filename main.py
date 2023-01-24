import sys
sys.path.append('./config')
import praw
import config


reddit = praw.Reddit(
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET,
    password=config.PASSWORD,
    user_agent=config.USER_AGENT,
    username=config.USERNAME,
)

for moderator in reddit.subreddit("news").moderator():
    print(moderator)