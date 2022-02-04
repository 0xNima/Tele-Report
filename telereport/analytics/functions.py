import os
import asyncio

from typing import Callable, Any

from django.core.cache import cache as django_cache
from django.conf import settings

from django_redis import get_redis_connection

from telethon import TelegramClient
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsSearch, UserStatusOnline


from updater import channel_username


def with_client(action: Callable[[TelegramClient, Any], Any]):
    """ Decorator function to pass telegram client to the action
    :param action: A callable which execute telegram functions
    :return: Any
    """
    async def wrapper(*args, **kwargs):
        async with await TelegramClient(
                'telereporter.session',  # path to .session. It will be created if does not exist
                api_hash=os.getenv('API_HASH'),
                api_id=int(os.getenv('API_ID')),
        ).start() as client:
            return await action(client, *args, **kwargs)
    return wrapper


@with_client
async def unban(client: TelegramClient, **kwargs):
    return await client(
        EditBannedRequest(
            channel_username, kwargs['user_id'], ChatBannedRights(
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


@with_client
async def ban(client: TelegramClient, **kwargs):
    return await client(
        EditBannedRequest(
            channel_username, kwargs['user_id'], ChatBannedRights(
                until_date=None,
                view_messages=True,
            )
        )
    )


@with_client
async def online_members(client: TelegramClient, request_hash: str):
    cache = get_redis_connection("default")

    pipe = cache.pipeline()

    offset = 0
    limit = settings.ONLINE_MEMBERS_OFFSET

    while True:
        # check if request still valid
        if request_hash != django_cache.get('rhash'):
            _bulk_remove(cache, pipe, request_hash)
            return

        response = await client(
            GetParticipantsRequest(
                channel_username, ChannelParticipantsSearch(''), offset, limit,
                hash=0
            )
        )

        if not response.users:
            _bulk_remove(cache, pipe, request_hash)
            return

        for i, user in enumerate(response.users):
            if isinstance(user.status, UserStatusOnline):
                pipe.set(
                    f'online_{request_hash}_{i + offset}',
                    f'{user.first_name} {user.last_name or ""} u:{user.username or ""}',
                )

        pipe.execute()
        pipe.reset()

        offset += len(response.users)

        await asyncio.sleep(settings.ONLINE_MEMBERS_POLLING_INTERVAL)


def _bulk_remove(cache, pipe, request_hash):
    CHUNK_SIZE = 1000
    cursor = '0'
    while cursor != 0:
        cursor, keys = cache.scan(cursor=cursor, match=f'online_{request_hash}_*', count=CHUNK_SIZE)
        if keys:
            pipe.delete(*keys)
    pipe.execute()
