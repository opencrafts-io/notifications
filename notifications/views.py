from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
import logging

from .models import Notification, UserProfile
from .serializers import BroadcastNotificationSerializer, NotificationSerializer, UserProfileOneSignalSerializer
from .utils import send_push_notification

logger = logging.getLogger(__name__)
CustomUser = get_user_model()

class NotificationListView(generics.ListAPIView):
    """
    API endpoint to list notifications for the authenticated user.
    Notifications are ordered by creation date (newest first).
    """
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Returns notifications belonging to the currently authenticated user.
        """
        UserProfile.objects.get_or_create(user=self.request.user)
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve or update a specific notification.
    Allows marking a notification as read (PATCH).
    Users can only access their own notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    queryset = Notification.objects.all()

    def get_queryset(self):
        """
        Ensures a user can only retrieve/update their own notifications.
        """
        return Notification.objects.filter(recipient=self.request.user)

class RegisterOneSignalPlayerIdView(generics.UpdateAPIView):
    """
    API endpoint for authenticated users to register or update their
    OneSignal player ID.
    """
    serializer_class = UserProfileOneSignalSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        """
        Retrieves or creates the UserProfile for the authenticated user.
        """
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        if created:
            logger.info(f"Created UserProfile for user: {self.request.user.email}")
        return user_profile

    def update(self, request, *args, **kwargs):
        """
        Performs the update of the OneSignal player ID.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"User {self.request.user.email} updated OneSignal Player ID to: {instance.external_id}")
        return Response(serializer.data, status=status.HTTP_200_OK)



class SendNotificationToUserView(generics.CreateAPIView):
    """
    API endpoint for sending push notifications to a single user.
    """
    permission_classes = [AllowAny]
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        recipient_user = validated_data.get('recipient') 
        
        if not recipient_user:
            return Response({"detail": "Recipient user is required."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = UserProfile.objects.filter(user=recipient_user).first()

        if not user_profile or not user_profile.external_id:
            logger.warning(f"User {recipient_user.id} has no OneSignal external ID. Notification not sent.")
            return Response(
                {"detail": "User does not have a registered push notification ID."},
                status=status.HTTP_400_BAD_REQUEST
            )
        notification = serializer.save()

        onesignal_payload_data = {
            "notification_id": str(notification.id),
            "url": notification.url,
            "name": notification.name,
            **(notification.data or {})
        }

        onesignal_response = send_push_notification(
            title=notification.title,
            message=notification.message,
            external_user_ids=[user_profile.external_id],
            data=onesignal_payload_data,
            url=notification.url,
            image_url=notification.image_url
        )

        if onesignal_response and "id" in onesignal_response:
            notification.onesignal_notification_id = onesignal_response['id']
            notification.save()
            logger.info(f"Notification sent to user {recipient_user.id}. OneSignal ID: {onesignal_response['id']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Failed to send notification to user {recipient_user.id}: {onesignal_response}")
            notification.delete()
            return Response(
                {
                    "detail": "Failed to send notification via OneSignal",
                    "onesignal_error": onesignal_response
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class SendBroadcastNotificationView(generics.CreateAPIView):
    """
    API endpoint for sending push notifications to OneSignal segments or using filters.
    Open for now. Add authentication later.
    """
    permission_classes = [AllowAny]
    serializer_class = BroadcastNotificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # validated_data = serializer.validated_data
        sent_by_user = request.user if request.user.is_authenticated else None
        broadcast_record = serializer.save(sent_by=sent_by_user)

        onesignal_payload_data = {
            "broadcast_id": str(broadcast_record.id), 
            "url": broadcast_record.url,
            "name": broadcast_record.name,
            **(broadcast_record.data or {})
        }
        
        onesignal_response = None
        if broadcast_record.included_segments:
            onesignal_response = send_push_notification(
                title=broadcast_record.title,
                message=broadcast_record.message,
                included_segments=broadcast_record.included_segments,
                data=onesignal_payload_data,
                url=broadcast_record.url,
                image_url=broadcast_record.image_url
            )
        else:
            onesignal_response = send_push_notification(
                title=broadcast_record.title,
                message=broadcast_record.message,
                filters=broadcast_record.filters,
                data=onesignal_payload_data,
                url=broadcast_record.url,
                image_url=broadcast_record.image_url
            )

        if onesignal_response and "id" in onesignal_response:
            onesignal_notification_id = onesignal_response['id']
            broadcast_record.onesignal_notification_id = onesignal_notification_id
            broadcast_record.save()

            logger.info(f"Broadcast notification sent. DB ID: {broadcast_record.id}, OneSignal ID: {onesignal_notification_id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Failed to send broadcast notification: {onesignal_response}. Deleting broadcast record {broadcast_record.id}")
            broadcast_record.delete()
            return Response(
                {
                    "detail": "Failed to send broadcast notification via OneSignal",
                    "onesignal_error": onesignal_response
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )