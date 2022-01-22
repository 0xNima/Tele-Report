from django.contrib import admin

from .models import Event, Message


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    change_list_template = 'events-list.html'

    def changelist_view(self, request, extra_context=None):
        urls = [
            ('Join', 'join'),
            ('Leave', 'leave'),
            ('Invite', 'invite'),
            ('Join By Invite', 'join-by-invite'),
        ]
        if extra_context is None:
            return super().changelist_view(request, extra_context={'event_urls': urls})

        extra_context.update({'event_urls': urls})

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    change_list_template = 'messages-list.html'

    def changelist_view(self, request, extra_context=None):
        urls = [
            ('Views', 'views'),
            ('Forwards', 'forwards'),
        ]
        if extra_context is None:
            return super().changelist_view(request, extra_context={'message_urls': urls})

        extra_context.update({'message_urls': urls})

        return super().changelist_view(request, extra_context=extra_context)
