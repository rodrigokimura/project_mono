from django import forms

from .models import Ship


class ShipForm(forms.ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Ship
        fields = '__all__'
        exclude = ['created_by']
        widgets = {}