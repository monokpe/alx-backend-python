from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission with granular controls:
    - User must be authenticated.
    - User must be a participant to view a conversation or its messages.
    - User must be the original SENDER to update or delete a message.
    """

    def has_permission(self, request, view):
        # FIX 1: Explicitly check for authentication first.
        if not request.user or not request.user.is_authenticated:
            return False

        if "conversation_pk" in view.kwargs:
            try:
                conversation = Conversation.objects.get(
                    pk=view.kwargs["conversation_pk"]
                )
                return request.user in conversation.participants.all()
            except Conversation.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        # FIX 1: Explicitly check for authentication first.
        if not request.user or not request.user.is_authenticated:
            return False

        # Determine the conversation based on the object type
        if isinstance(obj, Conversation):
            conversation = obj
        elif isinstance(obj, Message):
            conversation = obj.conversation
        else:
            return False  # Should not happen with our viewsets

        # The user must be a participant to do anything.
        is_participant = request.user in conversation.participants.all()
        if not is_participant:
            return False

        # FIX 2: If the object is a Message and the method is unsafe (PUT, PATCH, DELETE),
        # we add an additional check: is the user the original sender?
        if isinstance(obj, Message):
            # Safe methods (GET, HEAD, OPTIONS) are allowed for any participant.
            if request.method in permissions.SAFE_METHODS:
                return True
            # Unsafe methods are only allowed for the sender.
            return obj.sender == request.user

        # For Conversation objects, any participant has full permissions.
        return True
