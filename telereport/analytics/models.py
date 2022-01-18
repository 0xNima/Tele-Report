from django.db import models


class WithDateTime(models.Model):
    local_datetime = models.DateTimeField()
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        abstract = True


class Event(WithDateTime):
    event_id = models.BigIntegerField()
    event_type = models.SmallIntegerField()
    peer_id = models.BigIntegerField()


class Message(WithDateTime):
    message_id = models.BigIntegerField(primary_key=True)
    view_count = models.IntegerField(default=0)
    forward_count = models.IntegerField(default=0)


