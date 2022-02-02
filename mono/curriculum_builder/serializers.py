"""Curriculum Builder's serializers"""
from typing import Dict

from rest_framework import serializers

from .models import (
    Acomplishment, Company, Curriculum, Skill, SocialMediaProfile,
    WorkExperience,
)


class CompanySerializer(serializers.ModelSerializer):
    """Company serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Company
        fields = (
            'name',
            'description',
            'image',
            'created_by',
        )
        read_only_fields = []


class WorkExperienceSerializer(serializers.ModelSerializer):
    """WorkExperience serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    company = CompanySerializer()

    class Meta:
        model = WorkExperience
        fields = (
            'company',
            'job_title',
            'description',
            'started_at',
            'ended_at',
            'created_by',
        )
        read_only_fields = []

    def create(self, validated_data: Dict):
        transaction = WorkExperience.objects.create(
            company=validated_data.pop('company')['id'],
            **validated_data,
        )
        return transaction

    def update(self, instance: WorkExperience, validated_data: Dict):
        instance.company = validated_data.pop('company')['id']
        instance = super().update(instance, validated_data)
        return instance


class AcomplishmentSerializer(serializers.ModelSerializer):
    """Acomplishment serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    work_experience = WorkExperienceSerializer()

    class Meta:
        model = Acomplishment
        fields = (
            'work_experience',
            'title',
            'description',
            'created_by',
        )
        read_only_fields = []

    def create(self, validated_data: Dict):
        transaction = Acomplishment.objects.create(
            work_experience=validated_data.pop('work_experience')['id'],
            **validated_data,
        )
        return transaction

    def update(self, instance: Acomplishment, validated_data: Dict):
        instance.work_experience = validated_data.pop('work_experience')['id']
        instance = super().update(instance, validated_data)
        return instance


class SkillSerializer(serializers.ModelSerializer):
    """Skill serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Skill
        fields = (
            'name',
            'description',
            'image',
            'created_by',
        )
        read_only_fields = []


class SocialMediaProfileSerializer(serializers.ModelSerializer):
    """SocialMediaProfile serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = SocialMediaProfile
        fields = (
            'platform',
            'link',
            'created_by',
        )
        read_only_fields = []


class CurriculumSerializer(serializers.ModelSerializer):
    """Curriculum serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Curriculum
        fields = (
            'address',
            'first_name',
            'last_name',
            'profile_picture',
            'bio',
            'social_media_profiles',
            'skills',
            'work_experiences',
            'created_by',
        )
        read_only_fields = []
