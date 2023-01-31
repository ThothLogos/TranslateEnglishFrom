import sys
sys.path.append('./config')
import os
import re
import subprocess
import praw
import config

def main():
    reddit = praw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        password=config.PASSWORD,
        user_agent=config.USER_AGENT,
        username=config.USERNAME
        )
    try:
        if check_dependencies(): log_debug("Dependency check passed")
        # Check inbox for potential new translation requests
        for unread in reversed(list(reddit.inbox.unread())):
            parse_inbox_request(unread)
    except Exception as e:
        log_err(e)
        exit()

# Format we want to reply to: [ignored] /u/TranslateEnglishFrom [language] [ignored]
# TODO: You should have to say please? We shouldn't abandon civility towards machines. #Prepare
def parse_inbox_request(message):
    if f"/u/{config.USERNAME}" in message.body:
        lang_capture = re.search(f"(\/u\/{config.USERNAME}) (\w+)", message.body)
        if lang_capture:
            log_debug(f"Regex Capture: {lang_capture.group(0)}")
            requested_lang = lang_capture.group(0).split(' ')[1].lower().capitalize()
            if requested_lang in config.LANGUAGES:
                url = f"http://reddit.com{message.submission.permalink}"
                transcript = attempt_translation(url, message.id, requested_lang)
                #reply_valid_request(message, requested_lang, transcript)
                #message.mark_read()
        else:
            raise Exception("Language capture regex failed")
    else:
        log_process(f"Message from /u/{message.author} was not a valid request, marking as read")
        message.mark_read()


def reply_valid_request(message, language, transcript):
    log_process(f"Replying to /u/{message.author} for valid {language} request")
    message.reply(f"You requested a translation of {language}, Whisper returned:\n\n{transcript}")

def attempt_translation(url, id, lang):
    log_process(f"New Job: {url}")
    target_media = download_media(url, id, lang)
    log_process(f"Translating media file: {target_media}")
    whisper = subprocess.run([
        "whisper", target_media,
        "--language", lang,
        "--model", config.WHISPER_MODEL,
        "--task", "translate",
        "--output_dir", config.MEDIA_TEMPDIR],
        capture_output=True
    )
    if whisper.returncode == 0:
        log_process(f"COMPLETE - Translation of {target_media} complete")
        return '  \n'.join(whisper.stdout.decode('UTF-8').split('\n')) # Reddit line-break juggling
    else:
        raise Exception("Whisper exited non-zero")

def download_media(url, id, lang):
    filepath = f"{config.MEDIA_TEMPDIR}/{lang.lower()}_{id}.mp4"
    if file_already_exists(filepath): raise Exception("Requested file already downloaded, aborting")
    gettit = subprocess.run(["gettit", "-u", url, "-o", filepath], capture_output=True)
    if gettit.returncode != 0: raise Exception("gettit failed, exited non-zero")
    return filepath

def encode_subtitles(video):
    subbedpath = os.path.splittext(video)[0] + "_subbed" + os.path.splitext(video)[1]
    ffmpeg = subprocess.run(["ffpmeg", "-i", video, "-vf", f"subtitles={video}.srt", subbedpath],
        capture_output=True)
    if ffmpeg.returncode != 0: raise Exception("ffmpeg failed attempting to encode subs")
    return subbedpath

def file_already_exists(filepath):
    test = subprocess.run(["test", "-f", filepath], capture_output=True)
    return True if test.returncode == 0 else False

def check_dependencies():
    if subprocess.run(["which", "gettit"], capture_output=True).returncode != 0:
        raise Exception("Failed to find gettit, returns non-zero")
    if subprocess.run(["which", "whisper"], capture_output=True).returncode != 0:
        raise Exception("Failed to find whisper, returns non-zero")
    return True

def log_err(message):     print(f"  [ERROR]  {message}")
def log_debug(message):   print(f"  [DEBUG]  {message}")
def log_process(message): print(f"[PROCESS]  {message}")

if __name__ == "__main__":
    main()
