"""Curriculum Builder's serializers"""
from typing import Dict

from rest_framework import serializers

from .models import (
    Acomplishment, Company, Curriculum, Skill, SocialMediaProfile,
    WorkExperience,
)


class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(created_by=request.user)


class AcomplishmentSerializer(serializers.ModelSerializer):
    """Acomplishment serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Acomplishment
        fields = (
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


class WorkExperienceSerializer(serializers.ModelSerializer):
    """WorkExperience serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # company = CompanySerializer()
    acomplishments = AcomplishmentSerializer(many=True)

    class Meta:
        model = WorkExperience
        fields = (
            # 'company',
            'job_title',
            'description',
            'started_at',
            'ended_at',
            'created_by',
            'acomplishments',
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


class CompanySerializer(serializers.ModelSerializer):
    """Company serializer"""
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    work_experiences = WorkExperienceSerializer(many=True, required=False)
    curriculum = UserFilteredPrimaryKeyRelatedField(
        queryset=Curriculum.objects.all()
    )

    class Meta:
        model = Company
        fields = (
            'name',
            'description',
            'image',
            'curriculum',
            'work_experiences',
            'created_by',
        )
        read_only_fields = []


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
    social_media_profiles = SocialMediaProfileSerializer(many=True)
    skills = SkillSerializer(many=True)
    companies = CompanySerializer(many=True)

    class Meta:
        model = Curriculum
        fields = (
            'address',
            'first_name',
            'last_name',
            'profile_picture',
            'bio',
            'companies',
            'social_media_profiles',
            'skills',
            'created_by',
        )
