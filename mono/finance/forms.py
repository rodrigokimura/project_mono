from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from .models import Transaction, Group, Category, Account
from django.contrib.auth import get_user_model, forms as auth_forms

class AccountForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Description'})
        self.fields['belongs_to'].widget.attrs.update({'placeholder': 'Ammount'})
        self.fields['initial_balance'].widget.attrs.update({'placeholder': 'Initial balance'})
        self.fields['group'].widget.attrs.update({'class': 'ui dropdown'})
      
    class Meta:
        model = Account
        fields = '__all__'
        exclude = []
        widgets = {
            'type': forms.HiddenInput()
            # 'timestamp':forms.Select,
        }

class TransactionForm(forms.ModelForm):
    error_css_class = 'error'
    localized_fields = ['timestamp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({'placeholder': 'Description'})
        self.fields['ammount'].widget.attrs.update({'placeholder': 'Ammount'})
        self.fields['category'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['created_by'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['account'].widget.attrs.update({'class': 'ui dropdown'})
        # self.fields['type'].widget.attrs.update({'type': 'hidden'})
        self.fields['timestamp'].widget.attrs.update({'type': 'number'})

    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            'type': forms.HiddenInput()
            # 'timestamp':forms.Select,
        }

class GroupForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Name'})

    class Meta:
        model = Group
        fields = '__all__'
        exclude = []
        widgets = {
            # 'timestamp':forms.Select,
        }
        
class CategoryForm(forms.ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Category 
        fields = '__all__'
        exclude = ['created_by']
        widgets = {
            # 'timestamp':forms.Select,
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Name'})
        
    def save(self, *args, **kwargs): 
        category = self.instance
        category.created_by = self.request.user
        category.save()
        
        return super(CategoryForm, self).save(*args, **kwargs)
        
class UserForm(auth_forms.UserCreationForm):
    error_css_class = 'error'

    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Display name"
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields["email"].label = "Email address"
        self.fields['email'].widget.attrs.update({'placeholder': 'Email address'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
    
    def add_user_to_public_group(sender, instance, created, **kwargs):
        """Post-create user signal that adds the user to everyone group."""
        try:
            if created:
                instance.groups.add(Group.objects.get(name='Cliente'))
        except Group.DoesNotExist:
            pass

    #post_save.connect(add_user_to_public_group, sender=User)