from django.contrib import admin

from .models import Event, Message, KickList, OnlineUser


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    change_list_template = 'events-list.html'

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context={'event_urls': [
            ('Join', 'join'),
            ('Leave', 'leave'),
            ('Invite', 'invite'),
            ('Join By Invite', 'join-by-invite'),
        ]})


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    change_list_template = 'messages-list.html'

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context={'message_urls': [
            ('Views', 'views'),
            ('Forwards', 'forwards'),
        ]})


@admin.register(KickList)
class KickListAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'datetime')

    def username(self, obj):
        return obj.user.username

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name


@admin.register(OnlineUser)
class OnlineMembersAdmin(admin.ModelAdmin):
    change_list_template = 'online-list.html'
