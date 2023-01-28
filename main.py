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

# Format we want to reply to: [ignored] /u/TranslateEnglishFrom [language] [ignored]
# TODO: You should have to say please? We shouldn't abandon civility towards machines. #Prepare
def parse_summon_request(message):
  if f"/u/{config.USERNAME}" in message.body:
    print("[SUMMON]  /u/summoned")
    lang_capture_attempt = re.search('(\/u\/TranslateEnglishFrom) (\w+)', message.body)
    if lang_capture_attempt:
      print(f"[CAPTURE] Raw capture: {lang_capture_attempt.group(0)}")
      requested_lang = lang_capture_attempt.group(0).split(' ')[1]
      if requested_lang in config.LANGUAGES:
        print(f"[CAPTURE] FOUND! -- requested language {requested_lang} is valid")
        reply_valid_request(message, requested_lang)
      else:
        print(f"[ERROR] NOT FOUND -- Requested language: {requested_lang}")
        #reply_invalid_request(message, requested_lang)
    else:
      print("[ERROR] Language capture regex failed")
  else:
    print(f"[IGNORED] Message from {message.author} was not a tag, marking as read")
    #message.mark_read()
    return


def reply_valid_request(message, language):
  print(f"[REPLY]  Attempting to reply to {message.author} for valid {language} request")
  message.reply(f"You requested a translation of {language}")
  return

def attempt_translation(post):
  return


if __name__ == "__main__":
  main()
