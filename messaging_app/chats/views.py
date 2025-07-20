from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversations.

    Provides `list`, `create`, `retrieve`, `update`, and `destroy` actions.
    Ensures that users can only view and interact with conversations
    in which they are a participant.
    """

    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should only return conversations for the currently
        authenticated user.
        """
        user = self.request.user
        # Filter conversations where the user is a participant.
        return user.conversations.all().prefetch_related("participants", "messages")

    def perform_create(self, serializer):
        """
        Custom logic to create a conversation.

        The `ConversationSerializer` handles adding participants from `participant_ids`.
        We override this to ensure the currently authenticated user is always
        included as a participant.
        """
        conversation = serializer.save()
        # Ensure the user creating the conversation is also a participant.
        conversation.participants.add(self.request.user)
        conversation.save()


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Messages.

    Provides endpoints to create and list messages within conversations.
    Users can only list messages from conversations they are part of and can
    only send messages to those conversations.
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should only return messages from conversations that the
        currently authenticated user is a part of.
        """
        user = self.request.user
        # Filter messages based on conversations the user is a member of.
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer):
        """
        Automatically set the sender of the message to the currently
        authenticated user. This prevents users from sending messages
        on behalf of others.
        """
        conversation = serializer.validated_data["conversation"]

        # Security Check: Ensure the user is a participant of the conversation
        if self.request.user not in conversation.participants.all():
            # Although get_queryset prevents listing, this stops malicious POST requests.
            # Using Response directly to avoid raising a generic exception.
            # This logic might be better placed in a custom permission class for larger apps.
            return Response(
                {"detail": "You do not have permission to post in this conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Set the sender to the logged-in user and save the message.
        serializer.save(sender=self.request.user)
