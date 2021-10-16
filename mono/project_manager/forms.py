from django import forms

from .models import Board, Project
from .widgets import ToggleWidget


class ProjectForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        project = self.instance
        if project.pk is None:
            project.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = Project
        fields = [
            'name',
        ]


class BoardForm(forms.ModelForm):
    error_css_class = 'error' 

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.project = Project.objects.get(id=kwargs.pop("project_pk"))
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['assigned_to'].queryset = self.project.allowed_users

    def save(self, *args, **kwargs):
        board = self.instance
        if board.pk is None:
            board.created_by = self.request.user
            board.project = self.project
        return super().save(*args, **kwargs)

    class Meta:
        model = Board
        fields = [
            'name',
            'assigned_to',

            'tags_feature',
            'color_feature',
            'due_date_feature',
            'status_feature',
            'assignees_feature',
            'checklist_feature',
            'files_feature',
            'comments_feature',
            'time_entries_feature',

        ]
        widgets = {
            'tags_feature': ToggleWidget,
            'color_feature': ToggleWidget,
            'due_date_feature': ToggleWidget,
            'status_feature': ToggleWidget,
            'assignees_feature': ToggleWidget,
            'checklist_feature': ToggleWidget,
            'files_feature': ToggleWidget,
            'comments_feature': ToggleWidget,
            'time_entries_feature': ToggleWidget,
        }
