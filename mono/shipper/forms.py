"""Shipper's forms"""
from django import forms

from .models import Ship


class ShipForm(forms.ModelForm):
    """Ship form"""

    error_css_class = "error"

    class Meta:
        model = Ship
        fields = ["name_1", "name_2"]
        widgets = {}
