import redis
import os
import asyncpg

from serializers import event_deserializer, message_deserializer
from log import Logger

from telethon.tl import types

from dotenv import load_dotenv

load_dotenv()


logger = Logger(__name__, path='updater.log')


class APIInfo:
    ID = int(os.getenv('API_ID'))
    HASH = os.getenv('API_HASH')


class Cache:
    _POOL = None

    def __init__(self):
        if self.__class__._POOL is None:
            logger.info('initializing cache pool')

            self.__class__._POOL = redis.ConnectionPool(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=os.getenv('REDIS_PORT', 6973),
                db=os.getenv('REDIS_DB', 11)
            )
        self.connection = redis.Redis(connection_pool=self.__class__._POOL)

    def last_log_id(self):
        if last_log_id := self.connection.get('last_log_id'):
            return int(last_log_id.decode())
        return 0

    def pipe(self):
        return self.connection.pipeline()

    def transaction(self, fn, keys):
        return self.connection.transaction(fn, *keys, value_from_callable=False)


class DBManager:
    _POOL = None

    async def init(self):
        logger.info('initialize DB pool')

        self.__class__._POOL = await asyncpg.create_pool(
            database=os.getenv('DB_NAME'),
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=os.getenv('DB_PORT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS')
        )

    async def save_events(self, events):
        logger.info('saving events to DB')

        if self.__class__._POOL is None:
            await self.init()

        data = [
            (int(log_id), *event_deserializer(byte)) for log_id, byte in events.items()
        ]

        async with self.__class__._POOL.acquire() as connection:
            await connection.copy_records_to_table(
                'analytics_event',
                records=data,
                columns=['event_id', 'event_type', 'peer_id', 'local_datetime', 'date', 'time']
            )

    async def update_or_save_messages(self, messages):
        logger.info('saving messages to DB')

        if self.__class__._POOL is None:
            await self.init()

        data = [
            (int(msg_id), *message_deserializer(byte)) for msg_id, byte in messages.items()
        ]

        async with self.__class__._POOL.acquire() as connection:
            await connection.execute('''CREATE TEMPORARY TABLE IF NOT EXISTS _message(
                local_datetime timestamp with time zone NOT NULL,
                date date NOT NULL,
                "time" time without time zone NOT NULL,
                message_id bigint NOT NULL,
                view_count integer NOT NULL,
                forward_count integer NOT NULL
            )''')
            await connection.copy_records_to_table(
                '_message',
                records=data,
                columns=['message_id', 'view_count', 'forward_count', 'local_datetime', 'date', 'time']
            )
            await connection.execute('''
                INSERT INTO analytics_message (local_datetime, date, "time", message_id, view_count, forward_count)
                SELECT * FROM _message
                ON CONFLICT (message_id)
                DO UPDATE SET (view_count, forward_count) = (EXCLUDED.view_count, EXCLUDED.forward_count)
                WHERE analytics_message.view_count <> EXCLUDED.view_count OR analytics_message.forward_count <> EXCLUDED.forward_count
            ''')
            await connection.execute('''TRUNCATE TABLE _message''')


class Action:
    def __new__(cls, action):
        print(JOIN, LEAVE, INVITE, JOIN_BY_INVITE)
        if isinstance(action, types.ChannelAdminLogEventActionParticipantJoin):
            return JOIN
        if isinstance(action, types.ChannelAdminLogEventActionParticipantLeave):
            return LEAVE
        if isinstance(action, types.ChannelAdminLogEventActionParticipantInvite):
            return INVITE
        if isinstance(action, types.ChannelAdminLogEventActionParticipantJoinByInvite):
            return JOIN_BY_INVITE

        return None
