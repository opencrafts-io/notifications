from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    RegisterOneSignalPlayerIdView,
    SendNotificationToUserView,
    SendBroadcastNotificationView
)
app_name = 'notifications'
urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('profiles/register-onesignal-player/', RegisterOneSignalPlayerIdView.as_view(), name='register-onesignal-player-id'),
    path('notifications/send/', SendNotificationToUserView.as_view(), name='send-notification'),
    path('notifications/send-broadcast/', SendBroadcastNotificationView.as_view(), name='send-broadcast-notification'),
]