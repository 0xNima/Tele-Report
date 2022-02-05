import asyncio
import queue
import os
import sys
import threading
import logging
import signal

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger('django')


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def __init__(self, *args, **kwargs):
        if sys.argv.__contains__('runserver'):
            # without `--norelead` flag, django create 2 process. So ready() method is called twice.
            # By creating .queue file, we have control on creating Queue only once
            self.create_q = True if sys.argv.__contains__('--noreload') else os.path.exists(settings.Q_FILE_PATH)

            if self.create_q:
                logger.info('Creating Queue')
                self.queue = self.Q()
        super().__init__(*args, **kwargs)

    def ready(self):
        if hasattr(self, 'create_q'):
            if hasattr(self, 'queue'):
                logger.info('Queue thread starting...')
                threading.Thread(name='q-thread', target=self.queue.run, daemon=True).start()
            else:
                open(settings.Q_FILE_PATH, 'bw')

    class Q:
        def __init__(self, size=settings.Q_SIZE):
            self.q = queue.Queue(size)

        def put(self, obj):
            self.q.put(obj)

        async def consume(self):
            while True:
                if not self.q.empty():
                    logger.info(f'consuming Q - size:{self.q.qsize()}')
                    fn, arg = self.q.get_nowait()
                    await fn(arg)
                await asyncio.sleep(settings.Q_CONSUMING_INTERVAL)

        def run(self):
            asyncio.run(self.consume())


def sig_handler(signum, frame):
    try:
        os.remove(settings.Q_FILE_PATH)
    except FileNotFoundError:
        sys.exit(0)


for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, sig_handler)
