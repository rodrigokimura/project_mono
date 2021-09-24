from django import forms

from .models import List, Task


class ListForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        list = self.instance
        if list.pk is None:
            list.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = List
        fields = [
            'name',
        ]


class TaskForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['list'].widget.attrs.update({'class': 'ui dropdown'})

    def save(self, *args, **kwargs):
        task = self.instance
        if kwargs['list_pk'] is None:
            task.list = kwargs['list_pk']
        if task.pk is None:
            task.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = Task
        fields = [
            'description',
            'list',
        ]
