from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.db.models import Q


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Creates a notification when a new message is saved.
    """
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Before a message is saved, check if its content has changed.
    If so, log the old content to MessageHistory.
    """
    if instance.pk:
        try:
            original_message = Message.objects.get(pk=instance.pk)

            if original_message.content != instance.content:
                MessageHistory.objects.create(
                    message=original_message, old_content=original_message.content
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass

@receiver(post_delete, sender=User)
def delete_user_data(sender, instance, **kwargs):
    """
    When a user is deleted, clean up all related data.
    Note: While on_delete=CASCADE handles this at the DB level,
    this signal can be used for more complex cleanup or logging.
    """
    print(f"User {instance.username} is being deleted. Cleaning up associated data.")

    Message.objects.filter(Q(sender=instance) | Q(receiver=instance)).delete()
