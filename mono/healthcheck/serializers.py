from rest_framework.serializers import DateField, Serializer


class CommitsByDateSerializer(Serializer):
    """Serializer to get commits by date."""
    date = DateField()
