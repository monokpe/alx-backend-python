from rest_framework import permissions

class IsConversationParticipant(permissions.BasePermission):
    """
    Permission check to ensure the user is a participant of the conversation.
    This is used for Conversation objects.
    """
    def has_object_permission(self, request, view, obj):
        # `obj` here is a Conversation instance.
        return request.user in obj.participants.all()

class IsMessageSenderOrReadOnly(permissions.BasePermission):
    """
    Permission check for Messages.
    - Allows any participant to read the message.
    - Allows only the sender to edit or delete the message.
    
    Usage: permission_classes = [IsAuthenticated, IsMessageSenderOrReadOnly]
    """
    def has_object_permission(self, request, view, obj):
        # `obj` here is a Message instance.
        
        # First, check if the user is even in the conversation.
        is_participant = request.user in obj.conversation.participants.all()
        if not is_participant:
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.sender == request.user