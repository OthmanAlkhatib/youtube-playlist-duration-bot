from telethon import TelegramClient
import asyncio
import os

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
session = "othman"

username = ''

class clt():
    def __init__(self):
        self.global_client = None

    async def start(self):
        client = TelegramClient(session, API_ID, API_HASH)
        self.global_client = client

        await self.global_client.start()

    async def main(self):
        global username

        entity = await self.global_client.get_entity("https://t.me/ahsan_alhadeeth")
        search_user = await self.global_client.get_participants(entity, search=username)

        if len(search_user) >= 1:
            return 1
        else:
            return 0


c = clt()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(c.start())

def in_channel(name):
    global username
    username = name
    return loop.run_until_complete(c.main())
