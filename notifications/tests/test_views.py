import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from notifications.models import Notification, BroadcastNotification, UserProfile
from users.models import CustomUser

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(email="user@example.com", password="testpass123")

@pytest.fixture
def user_profile(user):
    return UserProfile.objects.create(user=user, onesignal_player_id="mock-player-id")

@patch("notifications.views.send_push_notification")
def test_send_notification_to_user_success(mock_send, api_client, user_profile):
    mock_send.return_value = {"id": "onesignal-123"}
    url = reverse("notifications:send-notification")
    payload = {
        "recipient": user_profile.user.id,
        "title": "Test Title",
        "message": "Test message",
        "type": "info"
    }
    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Notification.objects.filter(recipient=user_profile.user).exists()
    mock_send.assert_called_once()

@patch("notifications.views.send_push_notification")
def test_send_notification_no_player_id(mock_send, api_client, user):
    url = reverse("notifications:send-notification")
    payload = {
        "recipient": user.id,
        "title": "No Player",
        "message": "User has no player ID",
        "type": "info"
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "registered push notification ID" in response.data["detail"]
    mock_send.assert_not_called()

@patch("notifications.views.send_push_notification")
def test_send_notification_onesignal_failure(mock_send, api_client, user_profile):
    mock_send.return_value = {"error": "mock-failure"}
    url = reverse("notifications:send-notification")
    payload = {
        "recipient": user_profile.user.id,
        "title": "Fail",
        "message": "Simulate failure",
        "type": "info"
    }
    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert not Notification.objects.filter(recipient=user_profile.user).exists()
    mock_send.assert_called_once()

@pytest.mark.django_db
@patch("notifications.views.send_push_notification")
def test_send_broadcast_notification_segments(mock_send, api_client):
    mock_send.return_value = {"id": "broadcast-onesignal-id"}
    url = reverse("notifications:send-broadcast-notification")
    payload = {
        "title": "Broadcast",
        "message": "Broadcast msg",
        "type": "alert",
        "included_segments": ["Active Users"]
    }
    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert BroadcastNotification.objects.exists()
    mock_send.assert_called_once()

@pytest.mark.django_db
@patch("notifications.views.send_push_notification")
def test_send_broadcast_notification_failure(mock_send, api_client):
    mock_send.return_value = {"error": "something broke"}
    url = reverse("notifications:send-broadcast-notification")
    payload = {
        "title": "Fail Broadcast",
        "message": "Fail broadcast",
        "type": "alert",
        "filters": [{"field": "tag", "key": "role", "relation": "=", "value": "admin"}]
    }
    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert not BroadcastNotification.objects.exists()
    mock_send.assert_called_once()
