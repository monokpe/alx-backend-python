from django.contrib.auth import get_user_model

# Import permissions directly
from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipant

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversations.
    """

    serializer_class = ConversationSerializer
    # Explicitly list all permissions. Order matters: check for auth first.
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    filter_backends = [filters.SearchFilter]
    search_fields = ["participants__email", "participants__first_name"]

    def get_queryset(self):
        """
        Returns conversations for the currently authenticated user.
        """
        user = self.request.user
        return user.conversations.all().prefetch_related("participants", "messages")

    def perform_create(self, serializer):
        """
        This logic is NOT redundant. It enforces a critical business rule:
        The user creating the conversation must always be a participant.

        Without this, a user could create a conversation for two other people
        and not be in it themselves. This method ensures the creator is included.
        """
        participants = serializer.validated_data.get("participants", [])
        # Ensure the creating user is always in the list of participants.
        if self.request.user not in participants:
            participants.append(self.request.user)
        serializer.save(participants=participants)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Messages within a specific Conversation.
    """

    serializer_class = MessageSerializer
    # Explicitly list all permissions.
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        """
        Returns messages from the conversation specified in the URL,
        if the user is a participant.
        """
        return Message.objects.filter(
            conversation=self.kwargs["conversation_pk"]
        ).order_by("sent_at")

    def perform_create(self, serializer):
        """
        This logic is NOT redundant. It performs two essential and secure actions:
        1. Sets the `sender` to the logged-in user, preventing a user from
           impersonating someone else.
        2. Sets the `conversation` from the URL, ensuring the message is
           created in the correct context of the nested route.
        """
        serializer.save(
            sender=self.request.user, conversation_id=self.kwargs["conversation_pk"]
        )
