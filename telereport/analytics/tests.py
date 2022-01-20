import datetime

from django.db.models import Sum, Count
from django.test import TestCase
from .models import Message, Event
from .constants import JOIN, LEAVE


class MessageTestCase(TestCase):
    fixtures = ['messages.json']

    def test_most_view(self):
        msg_ids = Message.objects.all().order_by('-view_count').values_list('message_id', flat=True)
        self.assertEqual(
            list(msg_ids),
            [5, 3, 1, 4, 2]
        )

    def test_most_forward(self):
        msg_ids = Message.objects.all().order_by('-forward_count').values_list('message_id', flat=True)
        self.assertEqual(
            list(msg_ids),
            [5, 4, 2, 1, 3]
        )

    def test_most_view_by_date(self):
        dates = Message.objects.all().values('date').annotate(sum=Sum('view_count')).order_by('-sum').values_list(
            'date', flat=True)
        self.assertEqual(
            list(dates),
            [
                datetime.date.fromisoformat('2021-12-28'),
                datetime.date.fromisoformat('2021-12-27'),
                datetime.date.fromisoformat('2021-12-26')
            ]
        )

    def test_most_forward_by_date(self):
        dates = Message.objects.all().values('date').annotate(sum=Sum('forward_count')).order_by('-sum').values_list(
            'date', flat=True)
        self.assertEqual(
            list(dates),
            [
                datetime.date.fromisoformat('2021-12-26'),
                datetime.date.fromisoformat('2021-12-28'),
                datetime.date.fromisoformat('2021-12-27')
            ]
        )

    def test_most_view_by_hour(self):
        hours = Message.objects.all().values('time__hour').annotate(sum=Sum('view_count')).order_by(
            '-sum').values_list('time__hour', flat=True)
        self.assertEqual(
            list(hours),
            [21, 9, 13, 22]
        )

    def test_most_forward_by_hour(self):
        hours = Message.objects.all().values('time__hour').annotate(sum=Sum('forward_count')).order_by(
            '-sum').values_list('time__hour', flat=True)
        self.assertEqual(
            list(hours),
            [13, 21, 22, 9]
        )


class EventTestCase(TestCase):
    fixtures = ['events.json']

    def test_join_by_datetime(self):
        ids = Event.objects.filter(event_type=JOIN).order_by('-local_datetime').values_list('id', flat=True)
        self.assertEqual(
            list(ids),
            [10, 9, 8, 4, 2, 1]
        )

    def test_leave_by_datetime(self):
        ids = Event.objects.filter(event_type=LEAVE).order_by('-local_datetime').values_list('id', flat=True)
        self.assertEqual(
            list(ids),
            [7, 5, 6, 3]
        )

    def test_most_join_by_date(self):
        dates = Event.objects.filter(event_type=JOIN).values('date').annotate(count=Count('id')).order_by(
            '-count').values_list('date', flat=True)
        self.assertEqual(
            list(dates),
            [
                datetime.date.fromisoformat('2021-12-29'),
                datetime.date.fromisoformat('2021-12-26'),
                datetime.date.fromisoformat('2021-12-27'),
            ]
        )

    def test_most_leave_by_date(self):
        dates = Event.objects.filter(event_type=LEAVE).values('date').annotate(count=Count('id')).order_by(
            '-count').values_list('date', flat=True)
        self.assertEqual(
            list(dates),
            [
                datetime.date.fromisoformat('2021-12-28'),
                datetime.date.fromisoformat('2021-12-26'),
            ]
        )

    def test_most_join_by_time(self):
        times = Event.objects.filter(event_type=JOIN).values('time__hour').annotate(count=Count('id')).order_by(
            '-count').values_list('time__hour', flat=True)
        self.assertEqual(
            list(times),
            [23, 14, 13]
        )

    def test_most_leave_by_time(self):
        times = Event.objects.filter(event_type=LEAVE).values('time__hour').annotate(count=Count('id')).order_by(
            '-count').values_list('time__hour', flat=True)
        self.assertEqual(
            list(times),
            [20, 22]
        )
