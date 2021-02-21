from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth import get_user_model, forms as auth_forms
from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe
from .models import Transaction, Group, Category, Account, Icon


class CalendarWidget(Widget):
    template_name = 'ui_calendar.html'
    def get_context(self, name, value, attrs=None):
        return {'widget': {
            'name': name,
            'value': value,
        }}
    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

class IconWidget(Widget):
    template_name = 'ui_icon.html'
    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
            },
            'icon_list': Icon.objects.all()
        }
    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
        
class CategoryWidget(Widget):
    template_name = 'ui_category.html'
    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
            },
            'category_list': self.queryset
        }
    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
        
class ToggleWidget(Widget):
    template_name = 'ui_toggle.html'
    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
            },
        }
    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

class AccountForm(forms.ModelForm):
    error_css_class = 'error'
    current_balance = forms.FloatField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Description'})
        self.fields['belongs_to'].widget.attrs.update({'placeholder': 'Ammount'})
        self.fields['belongs_to'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['group'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['initial_balance'].widget.attrs.update({'placeholder': 'Initial balance'})
        if self.instance.pk is None:
            self.fields['current_balance'].widget = forms.HiddenInput()
        else:
            self.fields['current_balance'].widget.attrs.update({'value': self.instance.current_balance})
            
        print(type(self.instance.pk))
        
    def save(self, *args, **kwargs): 
        account = self.instance
        current_balance = self.cleaned_data['current_balance']
        if current_balance is not None:
            account.adjust_balance(current_balance, self.request.user)
        return super(AccountForm, self).save(*args, **kwargs)
        
    class Meta:
        model = Account
        fields = '__all__'
        exclude = []
        widgets = {}

class TransactionForm(forms.ModelForm):
    error_css_class = 'error'
    localized_fields = ['timestamp']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({'placeholder': 'Description'})
        self.fields['ammount'].widget.attrs.update({'placeholder': 'Ammount'})
        self.fields['category'].widget.queryset = Category.objects.filter(created_by=self.request.user)
        self.fields['account'].widget.attrs.update({'class': 'ui dropdown'})

    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ['created_by']
        widgets = {
            'type': forms.HiddenInput,
            'category': CategoryWidget,
            'timestamp': CalendarWidget,
            'active': ToggleWidget,
        }
    def save(self, *args, **kwargs): 
        category = self.instance
        category.created_by = self.request.user
        category.save()
        return super(TransactionForm, self).save(*args, **kwargs)

class GroupForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Name'})
        self.fields['members'].widget.attrs.update({'class': 'ui dropdown'})

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
            'icon':IconWidget,
            'active':ToggleWidget
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Name'})
        self.fields['description'].widget.attrs.update({'rows': 3})
        self.fields['description'].widget.attrs.update({'placeholder': 'Description'})
        self.fields['type'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['group'].widget.attrs.update({'class': 'ui dropdown'})
        
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