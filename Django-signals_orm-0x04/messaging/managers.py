class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter for unread messages.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_read=False)

    def for_user(self, user):
        """
        Returns unread messages for a specific user.
        """
        return self.get_queryset().filter(receiver=user)