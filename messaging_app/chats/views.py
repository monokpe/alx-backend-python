from django.contrib.auth import get_user_model

# Import the required modules, including status and filters
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversations.
    Provides `list`, `create`, `retrieve`, `update`, and `destroy` actions.
    """

    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
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
    Provides endpoints to create and list messages within conversations.
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view returns messages from conversations the user is a part of.
        It can be filtered by a 'conversation' query parameter.
        """
        user = self.request.user
        queryset = Message.objects.filter(conversation__participants=user)

        conversation_id = self.request.query_params.get("conversation", None)
        if conversation_id is not None:
            queryset = queryset.filter(conversation__id=conversation_id)

        return queryset.order_by("sent_at")

    def create(self, request, *args, **kwargs):
        """
        Override the default create method to add custom validation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.validated_data["conversation"]

        # Security Check: Ensure the user is a participant of the conversation.
        if request.user not in conversation.participants.all():
            # Use the status module to return a 403 FORBIDDEN response.
            return Response(
                {"detail": "You do not have permission to post in this conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Manually call perform_create and build the success response.
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        """
        Set the sender to the logged-in user. This is called by `create`.
        """
        serializer.save(sender=self.request.user)
