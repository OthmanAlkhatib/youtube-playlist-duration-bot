from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackContext
from telegram import Update
from googleapiclient.discovery import build
import isodate
import os
import logging
import sys

TOKEN = os.getenv("TOKEN")
MODE = os.getenv("MODE")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

if MODE == "dev":
    def run():
        logger.info("Start in DEV mode")
        updater.start_polling()
elif MODE == "prod":
    def run():
        logger.info("Start in PROD mode")
        updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 5000)), url_path=TOKEN,
                              webhook_url="https://{}.herokuapp.com/{}".format("ahsan-alhadeeth", TOKEN))
else:
    logger.error("No mode specified")
    sys.exit(1)

apiKey = 'AIzaSyAHWIK6ZyAobRCxygl_s5dIEtiscJ-XJVo'

playlist_URL = ""
youtube = build('youtube', 'v3', developerKey=apiKey)

def start_handler(update, context):
    update.message.reply_text("Please Send a Correct Youtube Playlist URL to Proccess.")

def check_url(update: Update, context: CallbackContext):
    url = update.message.text
    if '=' in url:
        playlist_URL = url[url.index('=')+1:]
    videos_ids = []
    videos_durations = []
    update.message.bot.send_message(update.message.chat_id, "Procssing...")
    # get_videos_ids()

videos_ids = []
def get_videos_ids(update: Update, context: CallbackContext, next=''):
    global playlist_URL
    try:
        url = update.message.text
        if '=' in url:
            playlist_URL = url[url.index('=') + 1:]

        playlist_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_URL,
            maxResults=50,
            pageToken=next
        )

        playlist_response = playlist_request.execute()

        for i in playlist_response['items']:
            video_id = i['contentDetails']['videoId']
            videos_ids.append(video_id)

        if 'nextPageToken' in list(playlist_response.keys()):
            nextPageToken = playlist_response['nextPageToken']
            get_videos_ids(next=nextPageToken)
        else:
            update.message.reply_text(str(len(videos_ids)) + " Videos Descoverd")
            whole_playlist_duration = get_videos_durations()
            update.message.reply_text(whole_playlist_duration)
    except Exception as error:
        update.message.reply_text("Sorry, Incorrect URL")
        print(error)

videos_durations = []
def get_videos_durations():
    for video_id in videos_ids:
        video_request = youtube.videos().list(
            part='contentDetails',
            id=video_id
        )
        video_response = video_request.execute()

        video_duration = video_response['items'][0]['contentDetails']['duration']
        videos_durations.append((video_duration))

    whole_playlist_duration = isodate.parse_duration(videos_durations[0])
    for i in range(1, len(videos_durations)):
        whole_playlist_duration += isodate.parse_duration(videos_durations[i])
    return str(whole_playlist_duration)

if __name__ == "__main__":
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))

    updater.dispatcher.add_handler(MessageHandler(Filters.all, get_videos_ids))

    run()