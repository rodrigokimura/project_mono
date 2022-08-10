"""Accounts' serializers"""
from __mono.utils import validate_file_size
from rest_framework.serializers import CharField, ModelSerializer, Serializer

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


class ChangePasswordSerializer(Serializer):
    """Change password serializer"""
    old_password = CharField(required=True)
    new_password = CharField(required=True)
    new_password_confirmation = CharField(required=True)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class FCMTokenSerializer(Serializer):
    """Firebase Cloud Messaging Token"""
    token = CharField(required=True)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class UserSerializer(ModelSerializer):
    """User serializer"""
    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
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
        if 'avatar' in validated_data:
            profile = instance.profile
            profile.avatar = validated_data['avatar']
            profile.save()
        return super().update(instance, validated_data)
