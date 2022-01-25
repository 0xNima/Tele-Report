import os

from telethon import TelegramClient
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights


from updater import channel_username


async def unban_user(user_id):
    async with await TelegramClient(
            'updater/telereporter.session',  # path to .session. It will be created if does not exist
            api_hash=os.getenv('API_HASH'),
            api_id=int(os.getenv('API_ID')),
    ).start() as client:
        await client(
            EditBannedRequest(
                channel_username, user_id, ChatBannedRights(
                    until_date=None,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_games=True,
                    send_gifs=True,
                    send_inline=True,
                    embed_links=True,
                    send_polls=True,
                    change_info=True,
                    pin_messages=True
                )
            )
        )


async def ban_user(user_id):
    async with await TelegramClient(
            'updater/telereporter.session',  # path to .session. It will be created if does not exist
            api_hash=os.getenv('API_HASH'),
            api_id=int(os.getenv('API_ID')),
    ).start() as client:
        await client(
            EditBannedRequest(
                channel_username, user_id, ChatBannedRights(
                    until_date=None,
                    view_messages=True,
                )
            )
        )
