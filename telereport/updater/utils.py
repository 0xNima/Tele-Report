import datetime

import redis
import os
import asyncpg

from serializers import event_deserializer, message_deserializer
from log import Logger


from dotenv import load_dotenv

load_dotenv()


logger = Logger(__name__, path='updater.log')


class Cache:
    _POOL = None

    def __init__(self):
        if self.__class__._POOL is None:
            logger.info('CACHE -> initializing pool')

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
        logger.info('DATABASE -> initializing pool')

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
        logger.info('DATABASE -> saving messages')

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

    async def update_or_save_tguser(self, users):
        logger.info('DATABASE -> update/save users')

        if self.__class__._POOL is None:
            await self.init()

        ids = []
        data = []

        for user in users:
            data.append((user.id, user.username, user.first_name, user.last_name))
            ids.append(user.id)

        async with self.__class__._POOL.acquire() as connection:
            await connection.execute('''CREATE TEMPORARY TABLE IF NOT EXISTS _tguser(
                chat_id bigint,
                username varchar(255),
                first_name varchar(255) NOT NULL,
                last_name varchar(255)
            )''')
            await connection.copy_records_to_table(
                '_tguser',
                records=data,
                columns=['chat_id', 'username', 'first_name', 'last_name']
            )
            await connection.execute('''
                INSERT INTO analytics_tguser (chat_id, username, first_name, last_name)
                SELECT * FROM _tguser
                ON CONFLICT (chat_id)
                DO UPDATE SET (username, first_name, last_name) = (EXCLUDED.username, EXCLUDED.first_name, EXCLUDED.last_name)
                WHERE analytics_tguser.username <> EXCLUDED.username OR analytics_tguser.first_name <> EXCLUDED.first_name OR analytics_tguser.last_name <> EXCLUDED.last_name 
            ''')
            await connection.execute('''TRUNCATE TABLE _tguser''')

        return ids

    async def save_kicked_members(self, kicked):
        logger.info('DATABASE -> saving kicked participants')

        if self.__class__._POOL is None:
            await self.init()

        ids = await self.update_or_save_tguser(kicked)

        data = [(datetime.datetime.now(), uid) for uid in ids]

        async with self.__class__._POOL.acquire() as connection:
            await connection.execute('''TRUNCATE TABLE analytics_kicklist''')

            await connection.copy_records_to_table(
                'analytics_kicklist',
                records=data,
                columns=['datetime', 'user_id']
            )
