from telethon import TelegramClient
import asyncio

api_id = "11771632"
api_hash = "2efc92a2cdbacebc0354b656111755ef"
session = "john"

username = ''

class clt():
    def __init__(self):
        self.global_client = None

    async def start(self):
        client = TelegramClient(session, api_id, api_hash)
        self.global_client = client
        # print('hello1')
        await self.global_client.start()

    async def main(self):
        global username

        # print('hello2')
        entity = await self.global_client.get_entity("https://t.me/ahsan_alhadeeth")
        search_user = await self.global_client.get_participants(entity, search=username)

        if len(search_user) >= 1:
            return 1
        else:
            return 0


client = clt()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(client.start())

def in_channel(name):
    global username
    username = name
    return loop.run_until_complete(client.main())
