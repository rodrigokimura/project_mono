"""Curriculum Builder's views"""
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Curriculum, SocialMediaProfile


class RootView(TemplateView):
    """
    App's first view.
    """
    template_name = "curriculum_builder/index.html"


class CurriculumListView(ListView):
    """
    List of user's curricula.
    """
    model = Curriculum
    paginate_by = 20
    template_name = 'curriculum_builder/curriculum_list.html'

    def get_queryset(self):
        return Curriculum.objects.filter(created_by=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['curriculum_modal'] = {
            'id': 'curriculum-modal',
            'fields': [
                {
                    'label': 'First name',
                    'name': 'first_name',
                    'type': 'text',
                },
                {
                    'label': 'Last name',
                    'name': 'last_name',
                    'type': 'text',
                },
                {
                    'label': 'Address',
                    'name': 'address',
                    'type': 'text',
                },
                {
                    'label': 'Bio',
                    'name': 'bio',
                    'type': 'textarea',
                },
            ]
        }
        return context


class CurriculumDetailView(DetailView):
    """
    Curriculum detail view.
    """
    model = Curriculum
    template_name = 'curriculum_builder/curriculum_detail.html'
    
    def get_template_names(self, *args, **kwargs):
        curriculum = self.get_object()
        return [f'curriculum_builder/styles/{curriculum.style}.html']


class CurriculumEditView(DetailView):
    """
    Curriculum edit view.
    """
    model = Curriculum
    template_name = 'curriculum_builder/curriculum_edit.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['company_modal'] = {
            'id': 'company-modal',
            'fields': [
                {
                    'name': 'name',
                    'type': 'text',
                },
                {
                    'name': 'description',
                    'type': 'textarea',
                },
            ]
        }
        context['work_experience_modal'] = {
            'id': 'work-experience-modal',
            'fields': [
                {
                    'label': 'Job title',
                    'name': 'job_title',
                    'type': 'text',
                },
                {
                    'label': 'Description',
                    'name': 'description',
                    'type': 'textarea',
                },
                {
                    'label': 'Started at',
                    'name': 'started_at',
                    'type': 'calendar',
                },
                {
                    'label': 'Ended at',
                    'name': 'ended_at',
                    'type': 'calendar',
                },
            ]
        }
        context['acomplishment_modal'] = {
            'id': 'acomplishment-modal',
            'fields': [
                {
                    'label': 'Title',
                    'name': 'title',
                    'type': 'text',
                },
                {
                    'label': 'Description',
                    'name': 'description',
                    'type': 'textarea',
                },
            ]
        }
        context['skill_modal'] = {
            'id': 'skill-modal',
            'fields': [
                {
                    'label': 'Name',
                    'name': 'name',
                    'type': 'text',
                },
                {
                    'label': 'Description',
                    'name': 'description',
                    'type': 'textarea',
                },
            ]
        }
        context['social_media_profile_modal'] = {
            'id': 'social-media-profile-modal',
            'fields': [
                {
                    'label': 'Platform',
                    'name': 'platform',
                    'type': 'dropdown',
                    'choices': SocialMediaProfile.Platform.choices,
                },
                {
                    'label': 'Link',
                    'name': 'link',
                    'type': 'text',
                },
            ]
        }
        context['style_choices'] = Curriculum.Style.choices
        return context
