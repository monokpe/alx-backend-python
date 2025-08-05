from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """
    Represents a direct message from one user to another.
    """

    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edited_messages",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        edited_status = "(edited)" if self.edited else ""
        return (
            f"From {self.sender.username} to {self.receiver.username} {edited_status}"
        )


class MessageHistory(models.Model):
    """
    Logs the original content of a message before it is edited.
    """

    message = models.ForeignKey(
        Message, related_name="history", on_delete=models.CASCADE
    )
    old_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for message ID {self.message.id} at {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ["-timestamp"]


class Notification(models.Model):
    """
    Represents a notification for a user about a new message.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} about message from {self.message.sender.username}"
