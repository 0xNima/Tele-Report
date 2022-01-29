from asgiref.sync import async_to_sync
from django.db import models

from .functions import unban, ban, online_members


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


class TGUser(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name or ""}'


class KickList(models.Model):
    user = models.OneToOneField(TGUser, on_delete=models.PROTECT, null=True)
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}'

    def delete(self, using=None, keep_parents=False):
        async_to_sync(unban)(self.user.chat_id)
        super().delete(using, keep_parents)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        async_to_sync(ban)(self.user.chat_id)
        super().save(force_insert, force_update, using, update_fields)


class OnlineUser(models.Model):
    user = models.OneToOneField(TGUser, on_delete=models.CASCADE)
