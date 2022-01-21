from django.db.models import Count
from django.views.generic import TemplateView

from .models import Event, Message
from .constants import CHART_RANGE_SIZE, JOIN, LEAVE, INVITE, JOIN_BY_INVITE


class EventTemplateView(TemplateView):
    template_name = 'events.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(self.__get_event_context())

        return context

    def __get_event_context(self):
        event_type = getattr(self.__class__, 'event_type')
        event_title = getattr(self.__class__, 'event_title')

        history = Event.objects.filter(event_type=event_type) \
                       .values('local_datetime').annotate(count=Count('id')) \
                       .order_by('-local_datetime')[:CHART_RANGE_SIZE]

        most_by_date = Event.objects.filter(event_type=event_type) \
                            .values('date').annotate(count=Count('id')) \
                            .order_by('-count')[:CHART_RANGE_SIZE]

        most_by_hour = Event.objects.filter(event_type=event_type) \
                            .values('time__hour').annotate(count=Count('id')) \
                            .order_by('-count')[:CHART_RANGE_SIZE]

        return {
            'event_title': event_title,
            'events_history': history,
            'events_most_by_date': most_by_date,
            'events_most_by_hour': most_by_hour
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
