from django import forms
from django.forms import ValidationError
from django.forms.widgets import Widget
from django.contrib.auth import login, authenticate, get_user_model, forms as auth_forms
from django.template import loader
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta, datetime
from faker import Faker
from faker.providers import lorem
from captcha.fields import ReCaptchaField
from random import randrange, randint
import pytz
from .models import BudgetConfiguration, Transaction, Group, Category, Account, Icon, Goal, Budget
    
User = get_user_model()

class CalendarWidget(Widget):
    template_name = 'widgets/ui_calendar.html'
    type = 'datetime'
    format = 'n/d/Y h:i A'
    
    def __init__(self, attrs=None, *args, **kwargs):
        super().__init__(attrs)

    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
                'placeholder': name.replace('_', ' '),
            },
            'type': self.type,
            'format': self.format,
            'LANGUAGE_EXTRAS': settings.LANGUAGE_EXTRAS,
        }
        
    def format_value(self, value):
        return value
    
    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

class IconWidget(Widget):
    template_name = 'widgets/ui_icon.html'
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

class ButtonsWidget(Widget):
    template_name = 'widgets/ui_buttons.html'
    def __init__(self, attrs=None, *args, **kwargs):
      self.choices = kwargs.pop('choices')
      super().__init__(attrs)
    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
                'choices': self.choices,
            },
        }
    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
        
class CategoryWidget(Widget):
    template_name = 'widgets/ui_category.html'
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
    template_name = 'widgets/ui_toggle.html'
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
        self.fields['group'].widget.attrs.update({'class': 'ui dropdown'})
        if self.instance.pk:
            if self.instance.owned_by != self.request.user:
                self.fields['group'].widget.attrs.update({'class': 'ui disabled dropdown'})

        self.fields['group'].queryset = Group.objects.filter(members=self.request.user)
        self.fields['initial_balance'].widget.attrs.update({'placeholder': 'Initial balance'})
        if self.instance.pk is None:
            self.fields['current_balance'].widget = forms.HiddenInput()
        else:
            self.fields['current_balance'].widget.attrs.update({'value': self.instance.current_balance})

    def clean(self):
        if self.instance.pk is not None:
            if self.instance.owned_by != self.request.user:
                if self.instance.group != self.cleaned_data['group']:
                    raise ValidationError("You don't have permission to change the group.")
        return self.cleaned_data

    def save(self, *args, **kwargs): 
        account = self.instance
        if account.pk is None:
            account.created_by = self.request.user
            account.owned_by = self.request.user
        current_balance = self.cleaned_data['current_balance']
        if current_balance is not None:
            account.adjust_balance(current_balance, self.request.user)
        return super(AccountForm, self).save(*args, **kwargs)
        
    class Meta:
        model = Account
        fields = '__all__'
        exclude = ['created_by', 'owned_by']
        widgets = {}

class TransactionForm(forms.ModelForm):
    error_css_class = 'error'
    
    #type=HiddenInput()
    type = forms.CharField(
        widget=ButtonsWidget(choices=Category.TRANSACTION_TYPES))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        owned_accounts = Account.objects.filter(owned_by=self.request.user)
        shared_accounts = Account.objects.filter(group__members=self.request.user)
        self.fields['description'].widget.attrs.update({'placeholder': _('Description')})
        self.fields['ammount'].widget.attrs.update({'placeholder': _('Ammount')})
        self.fields['category'].widget.queryset = Category.objects.filter(created_by=self.request.user, internal_type=Category.DEFAULT)
        self.fields['account'].queryset = (owned_accounts | shared_accounts).distinct()
        self.fields['account'].widget.attrs.update({'class': 'ui dropdown'})
        if self.instance.pk is not None:
            self.fields['type'].initial = self.instance.category.type
        else:
            self.fields['type'].initial = Category.EXPENSE
    
    def get_context_data(self, **kwargs):
        context = super(TransactionForm, self).get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        return context
        
    class Meta:
        model = Transaction
        fields = [
            "description",
            "timestamp",
            "account",
            "ammount",
            "category",
            "active",
        ]
        exclude = ['created_by']
        widgets = {
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
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Name'})

    class Meta:
        model = Group
        fields = '__all__'
        exclude = ['created_by', 'owned_by', 'members']
        widgets = {}
        
    def save(self, *args, **kwargs): 
        user = self.request.user
        if self.instance.id is None:
            self.instance.created_by = user
            self.instance.owned_by = user
        group = self.instance
        group.save()
        group.members.add(user)
        return super(GroupForm, self).save(*args, **kwargs)
        
class CategoryForm(forms.ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Category 
        fields = '__all__'
        exclude = ['created_by', 'internal_type']
        widgets = {
            'icon': IconWidget,
            'active': ToggleWidget
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

class IconForm(forms.ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Icon
        fields = '__all__'
        exclude = []
        widgets = {}
    def save(self, *args, **kwargs):
        icon = self.instance
        icon.markup = icon.markup.lower()
        return super(IconForm, self).save(*args, **kwargs)

class GoalForm(forms.ModelForm):
    error_css_class = 'error'
    
    class Meta:
        model = Goal
        fields = '__all__'
        exclude = ['created_by']
        widgets = {
            'start_date':CalendarWidget,
            'target_date':CalendarWidget,
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget.type = 'date'
        self.fields['start_date'].widget.format = 'n/d/Y'
        self.fields['target_date'].widget.type = 'date'
        self.fields['target_date'].widget.format = 'n/d/Y'
        self.fields['name'].widget.attrs.update({'placeholder': 'Name'})
        self.fields['group'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['progression_mode'].widget.attrs.update({'class': 'ui dropdown'})
        
    def save(self, *args, **kwargs):
        goal = self.instance
        if goal.id is None:
            goal.created_by = self.request.user
        goal.save()
        return super(GoalForm, self).save(*args, **kwargs)

class BudgetForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        shared_accounts = Account.objects.filter(group__members=self.request.user)
        owned_accounts = Account.objects.filter(owned_by=self.request.user, group=None)
        self.fields['accounts'].queryset = (shared_accounts|owned_accounts).distinct()
        self.fields['accounts'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['start_date'].widget.type = 'date'
        self.fields['start_date'].widget.format = 'n/d/Y'
        self.fields['end_date'].widget.type = 'date'
        self.fields['end_date'].widget.format = 'n/d/Y'
        created_categories = Category.objects.filter(
            created_by=self.request.user, 
            internal_type=Category.DEFAULT, 
            group=None,
            type=Category.EXPENSE)
        shared_categories = Category.objects.filter(
            group__members=self.request.user,
            type=Category.EXPENSE)
        self.fields['categories'].queryset = (shared_categories|created_categories).distinct()
        self.fields['categories'].widget.attrs.update({'class': 'ui dropdown'})

    def save(self, *args, **kwargs): 
        budget = self.instance
        if budget.pk is None:
            budget.created_by = self.request.user
        return super(BudgetForm, self).save(*args, **kwargs)
        
    class Meta:
        model = Budget
        fields = '__all__'
        exclude = ['configuration', 'created_by']
        widgets = {
            'start_date': CalendarWidget,
            'end_date': CalendarWidget,
        }

class BudgetConfigurationForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        shared_accounts = Account.objects.filter(group__members=self.request.user)
        owned_accounts = Account.objects.filter(owned_by=self.request.user, group=None)
        self.fields['accounts'].queryset = (shared_accounts|owned_accounts).distinct()
        self.fields['accounts'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['frequency'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['start_date'].widget.type = 'date'
        self.fields['start_date'].widget.format = 'n/d/Y'
        created_categories = Category.objects.filter(
            created_by=self.request.user, 
            internal_type=Category.DEFAULT, 
            group=None,
            type=Category.EXPENSE)
        shared_categories = Category.objects.filter(
            group__members=self.request.user,
            type=Category.EXPENSE)
        self.fields['categories'].queryset = (shared_categories|created_categories).distinct()
        self.fields['categories'].widget.attrs.update({'class': 'ui dropdown'})

    def save(self, *args, **kwargs): 
        budget = self.instance
        if budget.pk is None:
            budget.created_by = self.request.user
        return super(BudgetConfigurationForm, self).save(*args, **kwargs)
        
    class Meta:
        model = BudgetConfiguration
        fields = '__all__'
        exclude = ['created_by']
        widgets = {
            'active': ToggleWidget,
            'start_date': CalendarWidget,
        }
        
class UserForm(auth_forms.UserCreationForm):
    
    error_css_class = 'error'

    captcha = ReCaptchaField()
    email = forms.EmailField()

    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': self.fields["username"].label})
        self.fields['email'].widget.attrs.update({'placeholder': _("Email")})
        self.fields['password1'].widget.attrs.update({'placeholder': self.fields["password1"].label})
        self.fields['password2'].widget.attrs.update({'placeholder': self.fields["password2"].label})
        self.fields['captcha'].widget.api_params = {'hl': self.request.LANGUAGE_CODE}
    
    def clean(self):
       email = self.cleaned_data.get('email')
       if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists. Please use another one.")
       return self.cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            auth_user = authenticate(
                username=self.cleaned_data['username'], 
                password=self.cleaned_data['password1']
            )
            login(self.request, auth_user)

        return user

class FakerForm(forms.Form):

    class ContentTypeModelChoiceField(forms.ModelChoiceField):
        """Custom ModelChoiceField that displays the model name as options"""
        def label_from_instance(self, obj):
            return obj.model

    model = ContentTypeModelChoiceField(queryset=ContentType.objects.filter(app_label='finance'))
    batch_ammount = forms.IntegerField(max_value=100)
    target_user = forms.ModelChoiceField(User.objects.all())
    range_start = forms.DateField(required=False, widget=CalendarWidget)
    range_end = forms.DateField(required=False, widget=CalendarWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['target_user'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['range_start'].widget.type = 'date'
        self.fields['range_start'].widget.format = 'n/d/Y'
        self.fields['range_start'].widget.attrs.update({'placeholder': 'Range Start'})
        self.fields['range_end'].widget.type = 'date'
        self.fields['range_end'].widget.format = 'n/d/Y'
        self.fields['range_end'].widget.attrs.update({'placeholder': 'Range End'})

    def create_fake_instances(self):
        fake = Faker()
        fake.add_provider(lorem)

        batch_ammount = self.cleaned_data['batch_ammount']
        model = self.cleaned_data['model'].model
        target_user = self.cleaned_data['target_user']
        
        tz = pytz.timezone('UTC')

        if self.cleaned_data['range_start'] is not None:
            range_start = timezone.make_aware(datetime.combine(self.cleaned_data['range_start'], datetime.min.time()), tz)
        else:
            range_start = None

        if self.cleaned_data['range_end'] is not None:
            range_end = timezone.make_aware(datetime.combine(self.cleaned_data['range_end'], datetime.min.time()), tz)
        else:
            range_end = None


        def random_date(start, end):
            """
            This function will return a random datetime between two datetime 
            objects.
            """
            delta = end - start
            int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
            random_second = randrange(int_delta)
            r = start + timedelta(seconds=random_second)
            return r

        if model == 'transaction':
            for i in range(batch_ammount):
                if range_start is not None and range_end is not None:
                    timestamp = random_date(range_start, range_end)
                else:
                    timestamp = timezone.now()
                Transaction.objects.create(
                    description = fake.text(max_nb_chars=50, ext_word_list=None),
                    created_by = target_user,
                    timestamp = timestamp,
                    ammount = randint(0,1000),
                    category = Category.objects.filter(created_by=target_user, group=None, internal_type=Category.DEFAULT).order_by("?").first(),
                    account = Account.objects.filter(owned_by=target_user, group=None).order_by("?").first(),
                    # active = models.BooleanField(default=True)
                )

            success, message = True, {
                "level": messages.SUCCESS, 
                "message": f"Successfully created {batch_ammount} fake instances of model {model}"
            }
            return success, message

        else: 
            success, message = True, {
                "level": messages.ERROR, 
                "message": f"No fake generator implemented for model {model}"
            }
            return success, message

    
