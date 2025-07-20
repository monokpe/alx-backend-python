from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Conversation, Message


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used to represent User objects, excluding sensitive
    information like the password.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
        )
        read_only_fields = ("id", "role")


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    Includes the `sender`'s primary key for representation.
    The sender's full details can be optionally expanded in other serializers if needed.
    """

    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = (
            "id",
            "sender",
            "message_body",
            "sent_at",
            "conversation",
        )
        read_only_fields = ("id", "sent_at")


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.

    This serializer provides a comprehensive view of a conversation,
    including nested representations of its participants and all
    associated messages. This is ideal for fetching a full conversation
    history in a single API call.
    """

    # Use the UserSerializer to represent participants in a nested fashion.
    participants = UserSerializer(many=True, read_only=True)

    # Use the MessageSerializer to nest all messages within the conversation.
    # The `many=True` flag is crucial as a conversation has many messages.
    messages = MessageSerializer(many=True, read_only=True)

    # This field allows clients to specify participants by their IDs when creating a new conversation
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True, source="participants"
    )

    class Meta:
        model = Conversation
        fields = (
            "id",
            "participants",
            "messages",
            "created_at",
            "participant_ids",  # Field for creating conversations
        )
        read_only_fields = ("id", "created_at", "participants", "messages")

    def create(self, validated_data):
        """
        Custom create method to handle the creation of a conversation
        with the specified participants.
        """
        # The `participant_ids` field, with its `source='participants'`,
        # automatically populates the `participants` field.
        # We can now create the conversation instance with this data.
        conversation = Conversation.objects.create()
        conversation.participants.set(validated_data["participants"])
        return conversation
