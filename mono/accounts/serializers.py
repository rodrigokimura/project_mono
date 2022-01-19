from __mono.utils import validate_file_size
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from .models import UserProfile


class ProfileSerializer(ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            'avatar'
        ]

    def validate_avatar(self, f):
        return validate_file_size(f, 10)


class UserSerializer(ModelSerializer):
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
        p = instance.profile
        p.avatar = avatar
        p.save()
        return instance

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar')
        p = instance.profile
        p.avatar = avatar
        p.save()
        return super().update(instance, validated_data)
