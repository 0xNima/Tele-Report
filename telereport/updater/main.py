import asyncio
import os

from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsKicked

from utils import Cache, DBManager
from actions import Action
from serializers import event_serializer, message_serializer
from config import channel_username, poll_event_interval, iter_message_interval, save_events_interval, \
    save_msg_interval, poll_kicked_interval
from log import Logger

logger = Logger('main', path='updater.log')


async def poll_message_info(tl_client: TelegramClient):
    cache = Cache()

    pipe = cache.pipe()

    while True:
        logger.info('polling messages')

        async for message in tl_client.iter_messages(channel_username):
            local_datetime = message.date

            if (views_count := message.views) is None:
                continue

            if (forwards := message.forwards) is None:
                continue

            pipe.hset(
                'messages',
                message.id,
                message_serializer(
                    (views_count, forwards, local_datetime, local_datetime.date(), local_datetime.time())
                )
            )

        pipe.execute()

        await asyncio.sleep(iter_message_interval)


async def poll_participants_events(tl_client: TelegramClient):
    cache = Cache()

    pipe = cache.pipe()
    last_log_id = cache.last_log_id()

    while True:
        logger.info('polling events')

        is_set = False
        async for log in tl_client.iter_admin_log(channel_username, min_id=last_log_id):
            local_datetime = log.date
            log_id = log.id
            event_type = Action(log.action)

            if event_type is None:
                continue

            pipe.hset(
                'events',
                log_id,
                event_serializer(
                    (event_type, log.user_id, local_datetime, local_datetime.date(), local_datetime.time()))
            )

            if not is_set:
                last_log_id = log_id
                is_set = True

        pipe.set('last_log_id', last_log_id)
        pipe.execute()

        await asyncio.sleep(poll_event_interval)


async def poll_kicked_participants(tl_client: TelegramClient):
    while True:
        logger.info('polling kicked participants')

        kicked = await tl_client.get_participants(channel_username, filter=ChannelParticipantsKicked)

        if kicked:
            db = DBManager()
            await db.save_kicked_members(kicked)

        await asyncio.sleep(poll_kicked_interval)


class EventHolder:
    Data = dict()
    Save = 'save_events'


class MessageHolder:
    Data = dict()
    Save = 'update_or_save_messages'


async def save(key, holder, sleep_du):
    cache = Cache()
    db = DBManager()

    def transaction_fn(pipe):
        e = pipe.hgetall(key)
        pipe.delete(key)
        if e:
            holder.Data = e

    while True:
        await asyncio.sleep(sleep_du)

        cache.transaction(transaction_fn, [key])

        if holder.Data:
            await getattr(db, holder.Save)(holder.Data)
            holder.Data.clear()


async def start():
    client = await TelegramClient(
        'telereporter',
        api_hash=os.getenv('API_HASH'),
        api_id=int(os.getenv('API_ID'))
    ).start()
    await asyncio.gather(
        *[
            asyncio.create_task(poll_message_info(client)),
            asyncio.create_task(poll_participants_events(client)),
            asyncio.create_task(poll_kicked_participants(client)),
            asyncio.create_task(save('events', EventHolder, save_events_interval)),
            asyncio.create_task(save('messages', MessageHolder, save_msg_interval)),
        ]
    )


if __name__ == '__main__':
    asyncio.run(start())
