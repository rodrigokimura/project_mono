"""Curriculum Builder's serializers"""
from rest_framework import serializers

from .models import (
    Acomplishment,
    Company,
    Curriculum,
    Skill,
    SocialMediaProfile,
    WorkExperience,
)


class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """PrimaryKeyRelatedField filtered by user"""

    def get_queryset(self):
        request = self.context.get("request", None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(created_by=request.user)


class AcomplishmentSerializer(serializers.ModelSerializer):
    """Acomplishment serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    work_experience = UserFilteredPrimaryKeyRelatedField(
        queryset=WorkExperience.objects.all()
    )

    class Meta:
        model = Acomplishment
        fields = (
            "id",
            "title",
            "description",
            "created_by",
            "work_experience",
        )
        read_only_fields = []


class WorkExperienceSerializer(serializers.ModelSerializer):
    """WorkExperience serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    acomplishments = AcomplishmentSerializer(many=True, required=False)
    company = UserFilteredPrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = WorkExperience
        fields = (
            "id",
            "job_title",
            "description",
            "started_at",
            "ended_at",
            "created_by",
            "acomplishments",
            "company",
        )
        read_only_fields = []


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
            "id",
            "name",
            "description",
            "image",
            "started_at",
            "ended_at",
            "curriculum",
            "work_experiences",
            "created_by",
        )
        read_only_fields = (
            "started_at",
            "ended_at",
        )


class SkillSerializer(serializers.ModelSerializer):
    """Skill serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    curriculum = UserFilteredPrimaryKeyRelatedField(
        queryset=Curriculum.objects.all()
    )

    class Meta:
        model = Skill
        fields = (
            "id",
            "name",
            "description",
            "image",
            "created_by",
            "curriculum",
        )
        read_only_fields = []


class SocialMediaProfileSerializer(serializers.ModelSerializer):
    """SocialMediaProfile serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    curriculum = UserFilteredPrimaryKeyRelatedField(
        queryset=Curriculum.objects.all()
    )

    class Meta:
        model = SocialMediaProfile
        fields = (
            "id",
            "platform",
            "get_platform_display",
            "link",
            "created_by",
            "curriculum",
        )


class CurriculumSerializer(serializers.ModelSerializer):
    """Curriculum serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    social_media_profiles = SocialMediaProfileSerializer(
        many=True, required=False
    )
    skills = SkillSerializer(many=True, required=False)
    companies = CompanySerializer(many=True, required=False)

    class Meta:
        model = Curriculum
        fields = (
            "address",
            "first_name",
            "last_name",
            "profile_picture",
            "bio",
            "style",
            "companies",
            "social_media_profiles",
            "skills",
            "created_by",
        )
