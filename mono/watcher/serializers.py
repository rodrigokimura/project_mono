from rest_framework import serializers
from rest_framework.serializers import Serializer


class IssueResolverSerializer(Serializer):
    resolved = serializers.BooleanField()


class IssueIgnorerSerializer(Serializer):
    ignored = serializers.BooleanField()
