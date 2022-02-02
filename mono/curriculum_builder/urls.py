"""Curriculum Builder's urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import (
    AcomplishmentViewSet, CompanyViewSet, CurriculumViewSet, SkillViewSet,
    SocialMediaProfileViewSet, WorkExperienceViewSet,
)

app_name = 'curriculum_builder'

router = DefaultRouter()
router.register('acomplishments', AcomplishmentViewSet)
router.register('companies', CompanyViewSet)
router.register('curricula', CurriculumViewSet)
router.register('skills', SkillViewSet)
router.register('social_media_profiles', SocialMediaProfileViewSet)
router.register('work_experiences', WorkExperienceViewSet)

# pylint: disable=C0301
urlpatterns = [
    path("", views.RootView.as_view(), name='index'),
    path("api", include(router.urls))
]
