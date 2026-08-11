from ..models.notification import Notification


class NotificationService:
    async def send(self, user_id: int, message: str) -> Notification:
        # Placeholder: persist and send notification
        return Notification(id=1, user_id=user_id, message=message)


notification_service = NotificationService()
