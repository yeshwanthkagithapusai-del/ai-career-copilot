from django.urls import reverse
from .models import Notification
from career_intelligence.recommendations import RecommendationEngine

class NotificationService:
    """
    Handles generation of user notifications.
    Uses reference_id to prevent duplicates for deterministic events.
    """

    @staticmethod
    def create_notification(user, type, title, message, url=None, ref_id=None):
        if ref_id:
            # Prevent duplicates
            if Notification.objects.filter(user=user, reference_id=ref_id).exists():
                return None
                
        return Notification.objects.create(
            user=user,
            notification_type=type,
            title=title,
            message=message,
            action_url=url,
            reference_id=ref_id
        )

    @staticmethod
    def notify_milestone(user, event_name, detail, action_url, ref_id):
        """
        Standard wrapper for milestone completions.
        Checks RecommendationEngine to append the new Next Best Action.
        """
        message_parts = [detail]
        
        # Check if NBA changed or is relevant
        try:
            nba = RecommendationEngine.get_next_best_action(user)
            if nba and nba.action_type != "SETUP":
                message_parts.append(f"Your new Next Best Action is: {nba.title}")
        except Exception:
            pass # Fail safely, just omit NBA text if DB offline or error

        message = " ".join(message_parts)

        return NotificationService.create_notification(
            user=user,
            type="MILESTONE",
            title=event_name,
            message=message,
            url=action_url,
            ref_id=ref_id
        )
