import datetime

from django.db.models import Sum
from django.test import TestCase
from .models import Message, Event


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

