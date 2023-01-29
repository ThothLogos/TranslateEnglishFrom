import sys
sys.path.append('./config')
import re
import praw
import config

jobqueue = {}


def main():
    reddit = praw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        password=config.PASSWORD,
        user_agent=config.USER_AGENT,
        username=config.USERNAME,
    )
    # Check inbox for potential new translation requests
    for unread in reversed(list(reddit.inbox.unread())):
        parse_summon_request(unread)


# Format we want to reply to: [ignored] /u/TranslateEnglishFrom [language] [ignored]
# TODO: You should have to say please? We shouldn't abandon civility towards machines. #Prepare
def parse_summon_request(message):
    if f"/u/{config.USERNAME}" in message.body:
        lang_capture = re.search(f"(\/u\/{config.USERNAME}) (\w+)", message.body)
        if lang_capture:
            log_capture(f"Raw capture: {lang_capture.group(0)}")
            requested_lang = lang_capture.group(0).split(' ')[1].lower().capitalize()
            if requested_lang in config.LANGUAGES:
                log_capture(f"FOUND! -- requested language {requested_lang} is valid")
                url = f"http://reddit.com{message.submission.permalink}"
                reply_valid_request(message, requested_lang)
                attempt_translation(url, message.id, requested_lang)
                #message.mark_read()
            else:
                log_err(f"NOT FOUND -- Requested language: {requested_lang}")
                #reply_invalid_request(message, requested_lang)
        else:
            log_err("Language capture regex failed")
    else:
        log_ignored(f"Message from {message.author} was not a tag, marking as read")
        message.mark_read()
        return


def reply_valid_request(message, language):
    print(f"  [REPLY]  Replying to {message.author} for valid {language} request")
    #message.reply(f"You requested a translation of {language}")
    return

def attempt_translation(url, id, lang):
    log_process(f"Attempting to process: {url}")
    target_media = download_media(url, id, lang)
    log_process(f"Translating media file: {target_media}")
    return

def download_media(url, id, lang):
  dir = config.MEDIA_TEMPDIR
  filename = f"{lang.lower()}_{id}"
  filepath = f"{config.MEDIA_TEMPDIR}/{filename}"
  return filepath

def log_err(message):     print(f"  [ERROR]  {message}")
def log_reply(message):   print(f"  [REPLY]  {message}")
def log_capture(message): print(f"[CAPTURE]  {message}")
def log_process(message): print(f"[PROCESS]  {message}")
def log_ignored(message): print(f"[IGNORED]  {message}")

if __name__ == "__main__":
    main()
