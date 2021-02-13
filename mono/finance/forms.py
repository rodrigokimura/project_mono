from .models import Transaction
from django import forms

class TransactionForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({'placeholder': 'Phone'})
        self.fields['category'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['value'].widget.attrs.update({'placeholder': 'Avatar'})

    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            # 'description': Textarea(attrs={'cols': 80, 'rows': 20}),
        }
