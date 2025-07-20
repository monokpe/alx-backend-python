from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, filters
from .models import Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversations.

    Provides `list`, `create`, `retrieve`, `update`, and `destroy` actions.
    Ensures that users can only view conversations they are a participant in.
    Includes search functionality to find conversations by participant details.
    """

    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Add filter backends for searching capabilities.
    filter_backends = [filters.SearchFilter]

    # Define the fields on which searches can be performed.
    # This allows searching for conversations via participant email, first name, or last name.
    search_fields = [
        "participants__email",
        "participants__first_name",
        "participants__last_name",
    ]

    def get_queryset(self):
        """
        This view should only return conversations for the currently
        authenticated user.
        """
        user = self.request.user
        return user.conversations.all().prefetch_related("participants", "messages")

    def perform_create(self, serializer):
        """
        Custom logic to create a conversation.
        The user creating the conversation is always added as a participant.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        conversation.save()


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Messages.

    Provides endpoints to create and list messages.
    Users can only list messages from conversations they are part of.
    This viewset is enhanced to allow filtering messages by a specific
    conversation ID passed as a URL query parameter.
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view returns messages from conversations the user is a part of.

        It is enhanced to filter messages for a specific conversation if a
        `conversation` query parameter is provided in the URL.
        Example: `/api/messages/?conversation=<conversation_uuid>`
        """
        user = self.request.user
        queryset = Message.objects.filter(conversation__participants=user)

        # Get the conversation ID from the query parameters
        conversation_id = self.request.query_params.get("conversation", None)

        # If a conversation ID is provided, filter the queryset further
        if conversation_id is not None:
            # Filter the queryset to only include messages from the specified conversation
            queryset = queryset.filter(conversation__id=conversation_id)

        return queryset.order_by("sent_at")

    def perform_create(self, serializer):
        """
        Automatically set the sender to the currently authenticated user and
        validate that the user is a participant of the conversation.
        """
        conversation = serializer.validated_data["conversation"]

        # Security Check: Ensure the user is a participant of the conversation
        if self.request.user not in conversation.participants.all():
            raise permissions.PermissionDenied(
                {"detail": "You do not have permission to post in this conversation."}
            )

        serializer.save(sender=self.request.user)
