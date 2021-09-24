from django import forms
from django.contrib.auth import get_user_model

from .models import Note

User = get_user_model()


class NoteForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data

    def save(self, *args, **kwargs):
        note = self.instance
        if note.pk is None:
            note.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = Note
        fields = '__all__'
        exclude = ['created_by']
        widgets = {}
