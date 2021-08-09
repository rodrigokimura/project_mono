from django import forms
from .models import Project, Board
from .widgets import CalendarWidget, ToggleWidget


class ProjectForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['deadline'].widget.type = 'date'
        self.fields['deadline'].widget.format = 'n/d/Y'

    def save(self, *args, **kwargs):
        project = self.instance
        if project.pk is None:
            project.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = Project
        fields = [
            'name',
            'deadline',
            'active',
        ]
        widgets = {
            'deadline': CalendarWidget,
            'active': ToggleWidget,
        }


class BoardForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        project = Project.objects.get(id=kwargs.pop("project_pk"))
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['assigned_to'].queryset = project.allowed_users
        self.fields['project'].widget.attrs.update({'class': 'ui project dropdown'})
        self.fields['project'].queryset = Project.objects.filter(created_by=self.request.user)

    def save(self, *args, **kwargs):
        board = self.instance
        if board.pk is None:
            board.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = Board
        fields = [
            'name',
            'project',
            'assigned_to',
            'active',
        ]
        widgets = {
            'active': ToggleWidget,
        }
