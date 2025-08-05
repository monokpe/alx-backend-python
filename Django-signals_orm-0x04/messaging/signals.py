from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Creates a notification when a new message is saved.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )