import pytz
import uuid

from django.apps import apps
from django.conf import settings
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.core.cache import cache

from .apps import AnalyticsConfig
from .models import Event, Message
from .functions import online_members

from updater import JOIN, LEAVE, INVITE, JOIN_BY_INVITE, timezone


def unzip(qs, aggregate_key, change_tz=False):
    labels = []
    data = []

    for item in qs:
        data.append(item.pop(aggregate_key))
        if change_tz:
            labels.append(
                item.popitem()[1].astimezone(pytz.timezone(timezone)).strftime('%y-%m-%d %H:%M:%S')
            )
        else:
            labels.append(
                str(
                    item.popitem()[1]
                )
            )

    return labels, data


class EventTemplateView(TemplateView):
    template_name = 'events.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(self._get_event_context())

        return context

    def _get_event_context(self):
        event_type = getattr(self.__class__, 'event_type')
        event_title = getattr(self.__class__, 'event_title')

        history = Event.objects.filter(event_type=event_type) \
                       .values('local_datetime').annotate(count=Count('id')) \
                       .order_by('-local_datetime')[:settings.CHART_RANGE_SIZE]

        most_by_date = Event.objects.filter(event_type=event_type) \
                            .values('date').annotate(count=Count('id')) \
                            .order_by('-count')[:settings.CHART_RANGE_SIZE]

        most_by_hour = Event.objects.filter(event_type=event_type) \
                            .values('time__hour').annotate(count=Count('id')) \
                            .order_by('-count')[:settings.CHART_RANGE_SIZE]

        return {
            'event_title': event_title,
            'events_history': unzip(history, 'count', True),
            'events_most_by_date': unzip(most_by_date, 'count'),
            'events_most_by_hour': unzip(most_by_hour, 'count')
        }


class JoinEventView(EventTemplateView):
    event_type = JOIN
    event_title = 'Join Events'


class LeaveEventView(EventTemplateView):
    event_type = LEAVE
    event_title = 'Leave Events'


class InviteEventView(EventTemplateView):
    event_type = INVITE
    event_title = 'Invite Events'


class JoinByInviteEventView(EventTemplateView):
    event_type = JOIN_BY_INVITE
    event_title = 'Join By Invite Events'


class MessageTemplateView(TemplateView):
    template_name = 'messages.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(self._get_event_context())

        return context

    def _get_event_context(self):
        lookup_field = getattr(self.__class__, 'lookup_field')
        title = getattr(self.__class__, 'title')

        history = Message.objects.values('local_datetime').annotate(sum=Sum(lookup_field)) \
                         .order_by('-local_datetime')[:settings.CHART_RANGE_SIZE]

        most_by_date = Message.objects.values('date').annotate(sum=Sum(lookup_field)) \
                              .order_by('-sum')[:settings.CHART_RANGE_SIZE]

        most_by_hour = Message.objects.values('time__hour').annotate(sum=Sum(lookup_field)) \
                              .order_by('-sum')[:settings.CHART_RANGE_SIZE]

        return {
            'title': title,
            'history': unzip(history, 'sum', True),
            'most_by_date': unzip(most_by_date, 'sum'),
            'most_by_hour': unzip(most_by_hour, 'sum')
        }


class MessageViewsTemplateView(MessageTemplateView):
    lookup_field = 'view_count'
    title = 'View'


class MessageForwardsTemplateView(MessageTemplateView):
    lookup_field = 'forward_count'
    title = 'Forward'


class OnlineMembers(View):
    def get(self, request, *args, **kwargs):
        if request.GET.get('rhash'):
            pass
        else:
            rhash = uuid.uuid4().hex
            cache.set('rhash', rhash)
            apps.get_app_config(AnalyticsConfig.name).queue.put((online_members, rhash))
        return HttpResponse(status=200)
