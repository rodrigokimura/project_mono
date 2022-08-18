"""Curriculum Builder's viewsets"""
from __mono.permissions import IsCreator
from rest_framework.viewsets import ModelViewSet

from .models import (
    Acomplishment,
    Company,
    Curriculum,
    Skill,
    SocialMediaProfile,
    WorkExperience,
)
from .serializers import (
    AcomplishmentSerializer,
    CompanySerializer,
    CurriculumSerializer,
    SkillSerializer,
    SocialMediaProfileSerializer,
    WorkExperienceSerializer,
)

# pylint: disable=too-many-ancestors


class BaseViewSet(ModelViewSet):
    """Base viewset"""

    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            created_by=self.request.user,
        )


class CompanyViewSet(BaseViewSet):
    """Company viewset"""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class WorkExperienceViewSet(BaseViewSet):
    """WorkExperience viewset"""

    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer


class AcomplishmentViewSet(BaseViewSet):
    """Acomplishment viewset"""

    queryset = Acomplishment.objects.all()
    serializer_class = AcomplishmentSerializer


class SkillViewSet(BaseViewSet):
    """Skill viewset"""

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class SocialMediaProfileViewSet(BaseViewSet):
    """SocialMediaProfile viewset"""

    queryset = SocialMediaProfile.objects.all()
    serializer_class = SocialMediaProfileSerializer


class CurriculumViewSet(BaseViewSet):
    """Curriculum viewset"""

    queryset = Curriculum.objects.all()
    serializer_class = CurriculumSerializer
