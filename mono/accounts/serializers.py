from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.fields import ImageField
from rest_framework.serializers import ModelSerializer

from .models import UserProfile


class ProfileSerializer(ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            'avatar'
        ]

    def validate_avatar(self, f):
        file_size = f.size
        limit_mb = 10
        if file_size > limit_mb * 1024 * 1024:
            raise ValidationError("Max size of file is %s MiB" % limit_mb)
        return f


class UserSerializer(ModelSerializer):

    avatar = ImageField()
    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'avatar',
            'profile',
        ]

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
