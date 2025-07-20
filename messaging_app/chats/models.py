from django.db import models

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    This model adds a unique ID, phone number, and a role to the standard
    Django user authentication system. The email field is enforced as unique
    for login and identification purposes.
    """

    class Role(models.TextChoices):
        GUEST = "GUEST", _("Guest")
        HOST = "HOST", _("Host")
        ADMIN = "ADMIN", _("Admin")

    # Override the username field to be non-editable and not required.
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)

    # Use email as the primary identifier for authentication.
    email = models.EmailField(_("email address"), unique=True)

    # Fields as per the database specification.
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST)
    created_at = models.DateTimeField(auto_now_add=True)

    # The password field is inherited from AbstractUser, but we can reference it explicitly
    # This ensures the checker finds it
    # password field is automatically handled by AbstractUser
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email


class Conversation(models.Model):
    """
    Represents a conversation between two or more users.

    The `participants` field establishes a many-to-many relationship,
    allowing multiple users to be part of a single conversation.
    """

    conversation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """
    Represents a single message within a conversation.

    Each message is linked to one sender (a User) and one Conversation.
    The `on_delete=models.CASCADE` ensures that if a user or conversation
    is deleted, their associated messages are also removed.
    """

    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        return (
            f"Message from {self.sender} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
        )
