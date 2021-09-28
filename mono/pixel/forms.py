from django import forms

from .models import Site


class SiteForm(forms.ModelForm):

    error_css_class = 'error'

    class Meta:
        model = Site
        fields = ['host']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs) -> Site:
        site: Site = self.instance
        site.created_by = self.request.user
        return super().save(*args, **kwargs)
