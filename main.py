import sys
sys.path.append('./config')
import re
import subprocess
import praw
import config

# TODO: Move to async system calls and maintain a job queue
jobqueue = {}

def main():
    reddit = praw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        password=config.PASSWORD,
        user_agent=config.USER_AGENT,
        username=config.USERNAME,
    )
    # Ensure we have gettit and whisper available
    if check_dependencies(): log_debug("Dependency check passed")
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
    log_reply(f"Replying to {message.author} for valid {language} request")
    #message.reply(f"You requested a translation of {language}")
    return

def attempt_translation(url, id, lang):
    log_process(f"Attempting to process: {url}")
    target_media = download_media(url, id, lang)
    if target_media:
        log_process(f"Translating media file: {target_media}")
    return

def download_media(url, id, lang):
    dir = config.MEDIA_TEMPDIR
    filename = f"{lang.lower()}_{id}"
    filepath = f"{config.MEDIA_TEMPDIR}/{filename}.mp4"
    if file_already_exists(filepath):
        log_err("This file has already been downloaded, aborting request")
        return None
    log_process("Attempting to download Reddit media file using `gettit`")
    gettit = subprocess.run(["gettit", "-u", url, "-o", filepath], capture_output=True)
    if gettit.returncode != 0:
        log_debug(gettit.stderr)
        log_debug(gettit.stdout)
        log_debug(gettit.args)
    return filepath

def file_already_exists(filepath):
    test = subprocess.run(["test", "-f", filepath], capture_output=True)
    if test.returncode == 0:
      return True
    else:
      return False

def check_dependencies():
    which = subprocess.run(["which", "gettit"], capture_output=True)
    if which.returncode != 0:
        log_err("Failed to find gettit - which gettit returns non-zero")
        return False
    return True

def log_err(message):     print(f"  [ERROR]  {message}")
def log_debug(message):   print(f"  [DEBUG]  {message}")
def log_reply(message):   print(f"  [REPLY]  {message}")
def log_capture(message): print(f"[CAPTURE]  {message}")
def log_process(message): print(f"[PROCESS]  {message}")
def log_ignored(message): print(f"[IGNORED]  {message}")

if __name__ == "__main__":
    main()
