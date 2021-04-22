from django import forms
from tinymce.widgets import TinyMCE
from .models import Post


class PostForm(forms.ModelForm):
    error_css_class = 'error'

    class Meta:
        model = Post
        fields = '__all__'
        exclude = []
        widgets = {
            "content": TinyMCE(attrs={'cols': 80, 'rows': 30})
        }
