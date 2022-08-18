"""Curriculum Builder's urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import (
    AcomplishmentViewSet,
    CompanyViewSet,
    CurriculumViewSet,
    SkillViewSet,
    SocialMediaProfileViewSet,
    WorkExperienceViewSet,
)

app_name = "curriculum_builder"

router = DefaultRouter()
router.register("acomplishments", AcomplishmentViewSet)
router.register("companies", CompanyViewSet)
router.register("curricula", CurriculumViewSet)
router.register("skills", SkillViewSet)
router.register("social_media_profiles", SocialMediaProfileViewSet)
router.register("work_experiences", WorkExperienceViewSet)

urlpatterns = [
    path("", views.RootView.as_view(), name="index"),
    path(
        "curriculum/",
        views.CurriculumListView.as_view(),
        name="curriculum_list",
    ),
    path(
        "curriculum/<int:pk>/",
        views.CurriculumDetailView.as_view(),
        name="curriculum_detail",
    ),
    path(
        "curriculum/<int:pk>/edit/",
        views.CurriculumEditView.as_view(),
        name="curriculum_edit",
    ),
    path("api/", include(router.urls)),
]
