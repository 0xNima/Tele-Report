import asyncio
import queue
import os
import sys
import threading
import logging


from django.apps import AppConfig


logger = logging.getLogger('django')


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def __init__(self, *args, **kwargs):
        #   without --norelead flag, django create 2 process. So ready() method is called twice.
        #   By creating .queue file, we have control on creating Queue only once
        self.create_q = True if sys.argv.__contains__('--noreload') else os.path.exists('.queue')

        if self.create_q:
            logger.info('Creating Queue')
            self.queue = self.Q()

        super().__init__(*args, **kwargs)

    def ready(self):
        if hasattr(self, 'queue'):
            logger.info('Queue thread starting...')
            threading.Thread(target=self.queue.run).start()
            os.remove('.queue')     # the queue is already created, so we don't need to .queue
        else:
            open('.queue', 'bw')

    class Q:
        def __init__(self, size=5):
            self.q = queue.Queue(size)

        def put(self, obj):
            self.q.put(obj)

        async def consume(self):
            while True:
                if not self.q.empty():
                    logger.info(f'consuming Q - size:{self.q.qsize()}')
                    fn, arg = self.q.get_nowait()
                    await fn(arg)
                await asyncio.sleep(1)

        def run(self):
            asyncio.run(self.consume())
