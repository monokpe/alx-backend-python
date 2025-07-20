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
            "user_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
        )
        read_only_fields = ("user_id", "role")


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    Includes a read-only `sender_email` field for better representation in API responses,
    which satisfies the requirement for using serializers.CharField.
    """
    # Use CharField with `source` to display the sender's email in responses (read-only).
    # This provides more context than just returning the sender's ID.
    sender_email = serializers.CharField(source='sender.email', read_only=True)

    class Meta:
        model = Message
        fields = (
            "message_id",
            "sender",          # Used for write operations (creating a message)
            "sender_email",    # Used for read operations (displaying a message)
            "conversation",
            "message_body",
            "sent_at",
        )
        read_only_fields = ("message_id", "sent_at")
        # Make the 'sender' field write-only, as 'sender_email' is used for representation.
        extra_kwargs = {
            'sender': {'write_only': True}
        }


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.

    This serializer provides a comprehensive view of a conversation, including
    nested messages, participant details, and a custom summary field. It also
    includes validation to ensure a conversation has at least two participants.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # This write-only field allows clients to specify participants by ID during creation.
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=User.objects.all(),
        source='participants'
    )

    # Use SerializerMethodField to add custom, dynamically-generated data.
    # This field will provide a human-readable summary of the conversation.
    participant_summary = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "conversation_id",
            "participant_summary", # Custom summary field
            "participants",
            "messages",
            "created_at",
            "participant_ids",     # Write-only field for creation
        )
        read_only_fields = ("conversation_id", "created_at", "participants", "messages")

    def get_participant_summary(self, obj):
        """
        Generates a string listing the emails of the participants.
        `obj` is the Conversation instance being serialized.
        """
        # This method is automatically called by DRF for the `participant_summary` field.
        participant_emails = [user.email for user in obj.participants.all()]
        return f"Conversation between: {', '.join(participant_emails)}"

    def validate(self, data):
        """
        Provides custom object-level validation.
        """
        # The `participant_ids` field populates `data['participants']` because of `source`.
        participants = data.get('participants')
        if not participants or len(participants) < 2:
            # Use ValidationError to enforce business logic.
            raise serializers.ValidationError("A conversation requires at least two participants.")
        return data

    def create(self, validated_data):
        """
        Custom create method to handle the creation of a conversation
        with the specified participants.
        """
        # The `validate` method has already run, so we can safely access participants.
        participants = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation
