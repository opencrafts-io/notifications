# notifications/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model
from notifications.models import UserProfile, Notification
from django.utils import timezone

CustomUser = get_user_model()

@pytest.mark.django_db
@pytest.mark.unit
def test_user_profile_creation():
    user = CustomUser.objects.create_user(email='profile_test@example.com', password='password')
    profile = UserProfile.objects.create(user=user, onesignal_player_id='abc-123-def')

    assert profile.user == user
    assert profile.onesignal_player_id == 'abc-123-def'
    assert profile.created_at is not None
    assert profile.updated_at is not None
    assert str(profile) == f"Profile for {user.email}"

@pytest.mark.django_db
@pytest.mark.unit
def test_notification_creation():
    user = CustomUser.objects.create_user(email='notify_test@example.com', password='password')
    notification = Notification.objects.create(
        recipient=user,
        title="Test Title",
        message="This is a test message.",
        url="http://example.com/test",
        type="info",
        data={"key": "value"}
    )

    assert notification.recipient == user
    assert notification.title == "Test Title"
    assert notification.message == "This is a test message."
    assert notification.url == "http://example.com/test"
    assert notification.type == "info"
    assert notification.data == {"key": "value"}
    assert not notification.is_read
    assert notification.created_at is not None
    assert notification.updated_at is not None
    assert notification.onesignal_notification_id is None
    assert str(notification) == f"Notification for {user.email}: {notification.title}"

@pytest.mark.django_db
@pytest.mark.unit
def test_notification_is_read_update():
    user = CustomUser.objects.create_user(email='read_test@example.com', password='password')
    notification = Notification.objects.create(recipient=user, title="Read Me", message="Please read.")
    
    initial_updated_at = notification.updated_at
    # Simulate a small delay for updated_at to differ
    timezone.now() 

    notification.is_read = True
    notification.save()
    
    updated_notification = Notification.objects.get(id=notification.id)
    assert updated_notification.is_read
    assert updated_notification.updated_at > initial_updated_at

