import sys
sys.path.append('./config')
import re
import praw
import config


def main():
  reddit = praw.Reddit(
      client_id=config.CLIENT_ID,
      client_secret=config.CLIENT_SECRET,
      password=config.PASSWORD,
      user_agent=config.USER_AGENT,
      username=config.USERNAME,
  )

  for unread in reversed(list(reddit.inbox.unread())):
    parse_summon_request(unread)
    reply(unread)
    #unread.mark_read()


# Format we want to reply to: [ignored] /u/TranslateEnglishFrom [language] [ignored]
# TODO: You should have to say please? We shouldn't abandon civility towards machines. #Prepare
def parse_summon_request(message):
  if f"/u/{config.USERNAME}" in message.body:
    print("[SUMMON] /u/summoned")
    lang_capture_attempt = re.search('(\/u\/TranslateEnglishFrom) (\w+)', message.body)
    if lang_capture_attempt != None:
      print(f"[CAPTURE] {lang_capture_attempt.group(0)}")
    else:
      print("[ERROR] Language capture regex failed")

    #words = message.body.strip().split()
    #for lang in config.LANGUAGES:
    #  if lang in words:
    #    print(f"[SUMMON] Found requested language: {lang}")
    #    return lang
  else:
    print(f"[IGNORED] Message from {message.author} was not a tag")
    return


def reply(message):
  return

def attempt_translation(post):
  return


if __name__ == "__main__":
  main()


