from django.urls import path

from .views import JoinEventView, LeaveEventView, InviteEventView, JoinByInviteEventView


urlpatterns = [
    path('event/join/', JoinEventView.as_view()),
    path('event/leave/', LeaveEventView.as_view()),
    path('event/invite/', InviteEventView.as_view()),
    path('event/join-by-invite/', JoinByInviteEventView.as_view()),
]
