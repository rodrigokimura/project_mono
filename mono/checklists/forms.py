"""Todo lists' forms"""
from django import forms

from .models import Checklist


class ListForm(forms.ModelForm):
    """
    Todo list form
    """
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Save todo list
        """
        todo_list = self.instance
        if todo_list.pk is None:
            todo_list.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = Checklist
        fields = [
            'name',
        ]
