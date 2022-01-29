from django.urls import path

from .views import JoinEventView, LeaveEventView, InviteEventView, JoinByInviteEventView, MessageForwardsTemplateView, \
    MessageViewsTemplateView, OnlineMembers

urlpatterns = [
    path('event/join/', JoinEventView.as_view()),
    path('event/leave/', LeaveEventView.as_view()),
    path('event/invite/', InviteEventView.as_view()),
    path('event/join-by-invite/', JoinByInviteEventView.as_view()),
    path('message/views/', MessageViewsTemplateView.as_view()),
    path('message/forwards/', MessageForwardsTemplateView.as_view()),
    path('online/', OnlineMembers.as_view())
]