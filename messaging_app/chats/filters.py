import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    sender = django_filters.NumberFilter(field_name="sender__id", lookup_expr="exact")

    sent_after = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")

    sent_before = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ["sender", "sent_after", "sent_before"]
