from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    onesignal_player_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.email}"


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.URLField(max_length=500, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    data = models.JSONField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    onesignal_notification_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['onesignal_notification_id']),
        ]

    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.title}"


class BroadcastNotification(models.Model):
    """
    Stores details about a broadcast notification sent to OneSignal segments or filters.
    """
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.URLField(max_length=500, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    data = models.JSONField(blank=True, null=True)
    onesignal_notification_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    included_segments = models.JSONField(blank=True, null=True)
    filters = models.JSONField(blank=True, null=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='broadcast_notifications')


    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['-sent_at']),
            models.Index(fields=['type']),
            models.Index(fields=['sent_by']),
        ]

    def __str__(self):
        return f"Broadcast: '{self.title}' ({self.onesignal_notification_id or 'Pending'})"