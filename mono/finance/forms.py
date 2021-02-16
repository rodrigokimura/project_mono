from .models import Transaction
from django import forms
from django.contrib.admin.widgets import AdminDateWidget

class TransactionForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({'placeholder': 'Description'})
        self.fields['ammount'].widget.attrs.update({'placeholder': 'Ammount'})
        self.fields['category'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['created_by'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['account'].widget.attrs.update({'class': 'ui dropdown'})
        #self.fields['type'].widget.attrs.update({'type': 'hidden'})
        self.fields['timestamp'].widget.attrs.update({'type': 'number'})

    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            'type': forms.HiddenInput()
            # 'timestamp':forms.Select,
        }
