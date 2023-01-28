import sys
sys.path.append('./config')
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
    print(f"Replying to: [{unread.subject}] {unread.body}")
    prase_summon_request(unread.body)
    reply(unread)
    #unread.mark_read()


# Format we want to reply to: [ignored] /u/TranslateEnglishFrom [language] [ignored]
def prase_summon_request(message):
  print(f"Incoming body: {message}")
  message = message.strip()
  if 'TranslateEnglishFrom' in message:
    print("Name was tagged")
  if '/u/TranslateEnglishFrom' in message:
    print("Name was /u/tagged")
  return


def reply(message):
  return

if __name__ == "__main__":
  main()


