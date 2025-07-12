import pytest
import requests
from unittest.mock import patch
from notifications.utils import send_push_notification

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr("django.conf.settings.ONESIGNAL_APP_ID", "test-app-id")
    monkeypatch.setattr("django.conf.settings.ONESIGNAL_API_KEY", "test-api-key")

@patch("notifications.utils.requests.post")
def test_send_push_notification_with_player_ids(mock_post, mock_settings):
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "notif-id", "recipients": 1}

    response = send_push_notification(
        title="Hello",
        message="This is a test",
        player_ids=["player123"]
    )

    assert response["id"] == "notif-id"
    assert response["recipients"] == 1
    mock_post.assert_called_once()

@patch("notifications.utils.requests.post")
def test_send_push_notification_multiple_targets_error(mock_post, mock_settings):
    response = send_push_notification(
        title="Hello",
        message="This is a test",
        player_ids=["player1"],
        external_user_ids=["user1"]
    )

    assert "error" in response
    assert "Only one of" in response["error"]
    mock_post.assert_not_called()

@patch("notifications.utils.requests.post")
def test_send_push_notification_no_target(mock_post, mock_settings):
    response = send_push_notification(
        title="Missing Target",
        message="No one will get this"
    )

    assert "error" in response
    assert "No valid recipient target" in response["error"]
    mock_post.assert_not_called()

@patch("notifications.utils.requests.post")
def test_send_push_notification_external_user_ids(mock_post, mock_settings):
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "notif-ext-id", "recipients": 1}

    response = send_push_notification(
        title="External",
        message="Message for external user",
        external_user_ids=["user-123"]
    )

    assert response["id"] == "notif-ext-id"
    mock_post.assert_called_once()

@patch("notifications.utils.requests.post")
def test_send_push_notification_onesignal_error(mock_post, mock_settings):
    mock_response = mock_post.return_value
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
    mock_response.text = '{"errors": ["Bad request"]}'
    mock_response.json.return_value = {"errors": ["Bad request"]}

    response = send_push_notification(
        title="Error Test",
        message="This will fail",
        player_ids=["bad-id"]
    )

    assert "error" in response
