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
        raise e
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
                media_file = download_media(url, message.id, requested_lang)
                transcript = translate_media_file(media_file, requested_lang)
                reply_valid_request(message, requested_lang, transcript)
                message.mark_read()
                if is_video_file(media_file):
                    log_process("Detected video, encoding subtitles...")
                    subtitled_video = encode_subtitles(media_file)
                    log_process(f"Subtitled encoding finished: {subtitled_video}")
                else:
                    log_debug("Detected audio?")
        else:
            raise Exception("Language capture regex failed")
    else:
        log_process(f"Message from /u/{message.author} was not a valid request, marking as read")
        message.mark_read()

def reply_valid_request(message, language, transcript):
    log_process(f"Replying to /u/{message.author} for valid {language} request")
    message.reply(f"You requested a translation of {language}, Whisper returned:\n\n{transcript}")

# Returns Reddit-formatted WhisperAI transcript, appropriate for Message.reply()
def translate_media_file(file, language):
    log_process(f"Whisper [{language}]: {file}")
    whisper = subprocess.run([
        "whisper", file,
        "--language", language,
        "--model", config.WHISPER_MODEL,
        "--task", "translate",
        "--output_dir", config.MEDIA_TEMPDIR],
        capture_output=True
    )
    if whisper.returncode == 0:
        log_process(f"COMPLETE - Translation of {file} complete")
        return '  \n'.join(whisper.stdout.decode('UTF-8').split('\n')) # Reddit line-break juggling
    else:
        raise Exception("Whisper exited non-zero")

# Downloads and returns location of Reddit media file
def download_media(url, id, lang):
    filepath = f"{config.MEDIA_TEMPDIR}/{lang.lower()}_{id}.mp4"
    if file_exists(filepath): raise Exception("Requested file already downloaded, aborting")
    gettit = subprocess.run(["gettit", "-u", url, "-o", filepath], capture_output=True)
    if gettit.returncode != 0: raise Exception("gettit failed, exited non-zero")
    return filepath

# Re-encodes input video with hard-coded subtltes, returns location of subtitled file
def encode_subtitles(video):
    subbedpath = os.path.splitext(video)[0] + "_subbed" + os.path.splitext(video)[1]
    ffmpeg = subprocess.run(["ffmpeg", "-i", video, "-vf", f"subtitles={video}.srt", subbedpath],
        capture_output=True)
    if ffmpeg.returncode != 0: raise Exception("ffmpeg failed attempting to encode subs")
    return subbedpath

# We assume file is video if it has multiple media streams, 1 stream implies audio file
def is_video_file(file):
    ffp = subprocess.Popen(("ffprobe", "-v", "error", "-show_format", file), stdout=subprocess.PIPE)
    grep = subprocess.check_output(('grep', 'nb_streams'), stdin=ffp.stdout)
    nb_streams = grep.decode('UTF-8').strip().split('=')[1]
    return True if int(nb_streams) > 1 else False

def file_exists(filepath):
    test = subprocess.run(["test", "-f", filepath], capture_output=True)
    return True if test.returncode == 0 else False

def check_dependencies():
    required_utils = ['whisper', 'gettit', 'ffmpeg', 'ffprobe']
    for util in required_utils:
        if subprocess.run(["which", util], capture_output=True).returncode != 0:
            raise Exception(f"Failed to find {util} install, 'which {util}' returns non-zero")
    return True

def log_err(message):     print(f"  [ERROR]  {message}")
def log_debug(message):   print(f"  [DEBUG]  {message}")
def log_process(message): print(f"[PROCESS]  {message}")

if __name__ == "__main__":
    main()
