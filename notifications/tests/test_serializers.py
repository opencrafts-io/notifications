import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification, UserProfile
from notifications.serializers import NotificationSerializer, UserProfileOneSignalSerializer

CustomUser = get_user_model()

@pytest.mark.django_db
@pytest.mark.unit
def test_notification_serializer():
    user = CustomUser.objects.create_user(email='serializer_user@example.com', password='password')
    notification = Notification.objects.create(
        recipient=user,
        title="Serializer Test",
        message="Message content.",
        url="http://test.com",
        name="test_name",
        data={"some_key": "some_value"},
        is_read=True,
        onesignal_notification_id="os_id_123"
    )

    serializer = NotificationSerializer(notification)
    data = serializer.data

    assert data['id'] == notification.id
    assert data['recipient'] == user.id
    assert data['recipient_email'] == user.email
    assert data['title'] == "Serializer Test"
    assert data['message'] == "Message content."
    assert data['url'] == "http://test.com"
    assert data['name'] == "test_name"
    assert data['data'] == {"some_key": "some_value"}
    assert data['is_read'] is True
    assert data['created_at'] is not None
    assert data['updated_at'] is not None
    assert data['onesignal_notification_id'] == "os_id_123"

    # Test read_only_fields
    read_only_fields = ['created_at', 'updated_at', 'recipient_email', 'onesignal_notification_id']
    for field in read_only_fields:
        assert serializer.get_fields()[field].read_only is True


@pytest.mark.django_db
@pytest.mark.unit
def test_user_profile_onesignal_serializer_valid_data():
    user = CustomUser.objects.create_user(email='profile_serializer@example.com', password='password')
    profile = UserProfile.objects.create(user=user, external_id="old_player_id")

    data = {'external_id': 'new_player_id_456'}
    serializer = UserProfileOneSignalSerializer(instance=profile, data=data, partial=True)
    assert serializer.is_valid(raise_exception=True)
    
    updated_profile = serializer.save()

    assert updated_profile.external_id == 'new_player_id_456'
    assert UserProfile.objects.get(user=user).external_id == 'new_player_id_456'

@pytest.mark.django_db
@pytest.mark.unit
def test_user_profile_onesignal_serializer_missing_player_id():
    user = CustomUser.objects.create_user(email='missing_player@example.com', password='password')
    profile = UserProfile.objects.create(user=user)

    data = {}
    serializer = UserProfileOneSignalSerializer(instance=profile, data=data)
    
    assert not serializer.is_valid()
    assert 'external_id' in serializer.errors
    assert 'This field is required.' in serializer.errors['external_id']