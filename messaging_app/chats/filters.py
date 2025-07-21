import django_filters
from .models import Message


class MessageFilter(django_filters.FilterSet):
    """
    FilterSet for the Message model.
    """

    start_date = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    sender_email = django_filters.CharFilter(
        field_name="sender__email", lookup_expr="icontains"
    )

    class Meta:
        model = Message
        fields = ["start_date", "end_date", "sender_email"]
