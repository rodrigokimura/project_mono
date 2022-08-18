"""Blog's forms"""
from django import forms
from tinymce.widgets import TinyMCE

from .models import Post


class PostForm(forms.ModelForm):
    """Form for creating and updating posts"""

    error_css_class = "error"

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "author",
        ]
        widgets = {
            "content": TinyMCE(
                attrs={
                    "cols": 80,
                    "rows": 30,
                },
            )
        }
