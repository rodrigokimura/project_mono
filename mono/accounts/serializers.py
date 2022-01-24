"""Accounts' serializers"""
from __mono.utils import validate_file_size
from rest_framework.serializers import ModelSerializer

from .models import User, UserProfile


class ProfileSerializer(ModelSerializer):
    """User profile serializer"""

    class Meta:
        model = UserProfile
        fields = [
            'avatar'
        ]

    def validate_avatar(self, file):  # pylint: disable=no-self-use
        return validate_file_size(file, 10)


class UserSerializer(ModelSerializer):
    """User serializer"""
    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'profile',
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'read_only': True},
            'profile': {'read_only': True},
        }

    def create(self, validated_data):
        avatar = validated_data.get('avatar')
        instance = super().create(validated_data)
        profile = instance.profile
        profile.avatar = avatar
        profile.save()
        return instance

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar')
        profile = instance.profile
        profile.avatar = avatar
        profile.save()
        return super().update(instance, validated_data)
