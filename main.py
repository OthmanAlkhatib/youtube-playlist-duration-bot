from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackContext
from telegram import Update
from googleapiclient.discovery import build
import isodate
import os
import logging
import sys
import getMembers

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
                              webhook_url="https://{}.herokuapp.com/{}".format("youtube-playlist-duration-bot", TOKEN))
else:
    logger.error("No mode specified")
    sys.exit(1)

API_KEY = os.getenv("API_KEY")

youtube = build('youtube', 'v3', developerKey=API_KEY)


def start_handler(update, context):
    username = update.message.chat.username
    if username == None:
        update.message.reply_text("Please make a Username for you Account")
        return

    in_my_channel = getMembers.in_channel(username)
    if in_my_channel :
        update.message.reply_text("Send Any Youtube Playlist URL to Proccess.")
    else:
        update.message.reply_text("Please Subscribe in This Channel First @ahsan_alhadeeth and Try Again")

def get_videos_ids(update: Update, context: CallbackContext):
    username = update.message.chat.username
    if username == None:
        update.message.reply_text("Please make a Username for you Account")
        return
    if not getMembers.in_channel(username) :
        update.message.reply_text("Please Subscribe in This Channel First @ahsan_alhadeeth and Try Again")
        return

    playlist_URL = ""
    videos_ids = []
    try:
        url = update.message.text
        if '=' in url:
            playlist_URL = url[url.rindex('=') + 1:]

        playlist_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_URL,
            maxResults=50,
            pageToken=""
        )

        playlist_response = playlist_request.execute()

        for i in playlist_response['items']:
            video_id = i['contentDetails']['videoId']
            videos_ids.append(video_id)

        while 'nextPageToken' in list(playlist_response.keys()):
            nextPageToken = playlist_response['nextPageToken']
            next = nextPageToken

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

        update.message.reply_text(str(len(videos_ids)) + " Videos Discoverd...")
        # whole_playlist_duration,videos_urls = get_videos_durations(videos_ids)
        whole_playlist_duration = get_videos_durations(videos_ids)
        update.message.reply_text(whole_playlist_duration)
        # for i in range(len(videos_urls)):
        #     update.message.reply_text("{0} https://www.youtube.com/watch?v={1}".format(str(i)+"_", videos_urls[i]))

    except Exception as error:
        update.message.reply_text("Sorry, Incorrect URL")
        print(error)

def get_videos_durations(videos_ids):
    videos_durations = []
    # videos_urls = []
    for video_id in videos_ids:
        video_request = youtube.videos().list(
            part='contentDetails',
            id=video_id
        )
        video_response = video_request.execute()

        print(video_id)
        print(video_response['items'])
        try:
            video_duration = video_response['items'][0]['contentDetails']['duration']
            videos_durations.append(video_duration)
        except Exception as error:
            print(error)
        # video_url = video_response['items'][0]['id']
        # videos_urls.append(video_id)

    whole_playlist_duration = isodate.parse_duration(videos_durations[0])
    for i in range(1, len(videos_durations)):
        whole_playlist_duration += isodate.parse_duration(videos_durations[i])
    # return str(whole_playlist_duration), videos_urls
    return str(whole_playlist_duration)

if __name__ == "__main__":
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))

    updater.dispatcher.add_handler(MessageHandler(Filters.all, get_videos_ids))

    run()
