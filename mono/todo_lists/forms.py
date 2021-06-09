from django import forms
from .models import List, Item


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


class ItemForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['list'].widget.attrs.update({'class': 'ui dropdown'})

    def save(self, *args, **kwargs):
        item = self.instance
        if kwargs['list_pk'] is None:
            item.list = kwargs['list_pk']
        if item.pk is None:
            item.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = Item
        fields = [
            'description',
            'list',
        ]
