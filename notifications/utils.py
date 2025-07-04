from django.conf import settings
import requests
import json
import os
import logging

logger = logging.getLogger(__name__)

# ONESIGNAL_APP_ID = settings.ONESIGNAL_APP_ID
# ONESIGNAL_REST_API_KEY = os.environ.get("ONESIGNAL_REST_API_KEY")

def send_push_notification(title, message, player_ids=None, external_user_ids=None, included_segments=None, filters=None, data=None, url=None):
    """
    Sends a push notification using the OneSignal API.

    Args:
        title (str): The title of the notification.
        message (str): The main message content.
        player_ids (list, optional): A list of OneSignal player IDs to target.
                                     Mutually exclusive with external_user_ids, included_segments, filters.
        external_user_ids (list, optional): A list of external user IDs (your internal user IDs).
                                            Mutually exclusive with player_ids, included_segments, filters.
        included_segments (list, optional): A list of OneSignal segment names (e.g., ["Active Users"]).
                                            Mutually exclusive with player_ids, external_user_ids, filters.
        filters (list, optional): A list of OneSignal filter objects for dynamic targeting.
                                  Mutually exclusive with player_ids, external_user_ids, included_segments.
                                  Example: [{"field": "tag", "key": "level", "relation": ">", "value": "10"}]
        data (dict, optional): Custom data to send with the notification.
        url (str, optional): A URL to open when the notification is clicked.

    Returns:
        dict: The JSON response from the OneSignal API, or an error dictionary.
    """
    if not settings.ONESIGNAL_APP_ID or not settings.ONESIGNAL_API_KEY:
        logger.error("OneSignal APP_ID or REST_API_KEY not configured.")
        return {"error": "OneSignal not configured."}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {settings.ONESIGNAL_API_KEY}"
    }

    payload = {
        "app_id": settings.ONESIGNAL_APP_ID,
        "contents": {"en": message},
        "headings": {"en": title},
        "target_channel": "push",
    }
    included_aliases = {}

    if data:
        payload["data"] = data
    if url:
        payload["url"] = url

    # Determine targeting
    target_count = sum([
        1 if player_ids else 0,
        1 if external_user_ids else 0,
        1 if included_segments else 0,
        1 if filters else 0
    ])

    if target_count > 1:
        logger.error("Multiple targeting parameters provided to send_push_notification. Only one is allowed.")
        return {"error": "Only one of player_ids, external_user_ids, included_segments, or filters can be used."}
    elif player_ids:
        payload["include_player_ids"] = player_ids
    elif external_user_ids:
        included_aliases["external_id"] = external_user_ids
        payload["include_aliases"] = included_aliases
    elif included_segments:
        payload["included_segments"] = included_segments
    elif filters:
        payload["filters"] = filters
    else:
        logger.warning("OneSignal push notification called without valid recipient target (player_ids, external_user_ids, included_segments, or filters).")
        return {"error": "No valid recipient target provided."}

    try:
        print(f"hereeeeeeeeeeeeeeeeeeeee!!!!!!!!!!!!!!!! : {payload}")
        response = requests.post(
            "https://onesignal.com/api/v1/notifications",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending OneSignal notification: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"OneSignal API Error Response: {e.response.text}")
            return {"error": str(e), "onesignal_response": e.response.json() if e.response.text else {}}
        return {"error": str(e)}