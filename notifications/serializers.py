# notifications/serializers.py
from rest_framework import serializers
from .models import BroadcastNotification, Notification, UserProfile
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    recipient_email = serializers.ReadOnlyField(source='recipient.email')

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_email', 'title', 'message', 'url', 'image_url',
            'name', 'data', 'is_read', 'created_at', 'updated_at', 'onesignal_notification_id'
        ]
        read_only_fields = ['id', 'recipient_email', 'created_at', 'updated_at', 'onesignal_notification_id']

class BroadcastNotificationSerializer(serializers.ModelSerializer):
    included_segments = serializers.JSONField(required=False, allow_null=True)
    filters = serializers.JSONField(required=False, allow_null=True)
    data = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = BroadcastNotification
        fields = ['id','title','message','url','image_url','name','data','included_segments','filters','sent_by','onesignal_notification_id','sent_at']
        read_only_fields = ['id', 'sent_at', 'onesignal_notification_id']

    def validate(self, data):
        """
        Custom validation to ensure either included_segments or filters is provided, but not both.
        """
        segment_names = data.get('included_segments')
        filters = data.get('filters')

        if not segment_names and not filters:
            raise serializers.ValidationError("Either 'included_segments' (list of strings) or 'filters' (OneSignal filter JSON) is required.")
        
        if segment_names and filters:
            raise serializers.ValidationError("Cannot specify both 'included_segments' and 'filters'. Choose one.")

        return data

class UserProfileOneSignalSerializer(serializers.ModelSerializer):
    external_id = serializers.CharField(
        max_length=255, 
        required=True,
        allow_null=False,
    )
    class Meta:
        model = UserProfile
        fields = ['external_id']
        extra_kwargs = {
            'external_id': {'required': True, 'allow_null': False}
        }