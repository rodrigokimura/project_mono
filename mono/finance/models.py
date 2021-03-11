from django.conf import settings
from django.db import models
from django.db.models import signals, Sum
from django.db.models.enums import Choices
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.urls import reverse
from django.template.loader import get_template
from datetime import timedelta
import jwt

User = get_user_model()

INCOME = 'INC'
EXPENSE = 'EXP'
TRANSACTION_TYPES = [
    (INCOME, 'Income'),
    (EXPENSE, 'Expense'),
]

class Transaction(models.Model):
    description = models.CharField(max_length=50, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ammount = models.FloatField()
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, default=EXPENSE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    
    @property
    def signed_ammount(self):
        sign = 1
        if self.type == 'EXP':
            sign = -1
        return self.ammount*sign
        
    def __str__(self) -> str:
        return self.description

class Icon(models.Model):
    markup = models.CharField(max_length=50, unique=True)
    def __str__(self) -> str:
        return self.markup

class Category(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, default=EXPENSE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
    @property
    def is_user_defined(self):
        return self.created_by is not None
    
    @property
    def is_group_defined(self):
        return self.group is not None
        
    @property
    def is_deletable(self):
        return self.is_group_defined or self.created_by
        
class Group(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groupset")
    owned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_groupset")
    members = models.ManyToManyField(User, related_name="shared_groupset")
    def __str__(self) -> str:
        return self.name
        
    def change_ownership_to(self, user):
        self.owned_by = user
        self.save()

class Account(models.Model): 
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="created_accountset", null=True)
    owned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_accountset")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    initial_balance = models.FloatField(default=0)
    
    @property
    def is_shared(self):
        return self.group is not None
    
    @property
    def current_balance(self):
        qs = Transaction.objects.filter(account=self.pk)
        sum = self.initial_balance
        for t in qs:
            sum += t.signed_ammount
        return sum
    
    @property
    def total_transactions(self):
        qs = Transaction.objects.filter(account=self.pk)
        return qs.count()
        
    def adjust_balance(self, target, user):
        diff = target - self.current_balance
        if diff < 0:
            type = "EXP"
        elif diff > 0:
            type = "INC"
        else:
            return
        transaction = Transaction(ammount=abs(diff))
        transaction.type = type
        transaction.description = "Balance adjustment"
        transaction.account = self
        transaction.created_by = user
        transaction.save()
        
    def remove_group(self):
        self.group = None
        self.save()
        
    def __str__(self) -> str:
        return self.name

WEEKLY = 'W'
MONTHLY = 'M'
YEARLY = 'Y'
GOAL_FREQUENCY = [
    (WEEKLY, 'Weekly'),
    (MONTHLY, 'Monthly'),
    (YEARLY, 'Yearly'),
]

OPEN = 'O'
PENDING = 'P'
CLOSED = 'C'
BUDGET_STATUS = [
    (OPEN, 'Open'),
    (PENDING, 'Pending'),
    (CLOSED, 'Closed'),
]

CONSTANT = 'C'
LINEAR = 'L'
PROGRESSION_MODES = [
    (CONSTANT, 'Constant'),
    (LINEAR, 'Linear'),
]

class Goal(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField()
    target_ammount = models.FloatField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    progression_mode = models.CharField(max_length=1, choices=PROGRESSION_MODES, default=CONSTANT)
    frequency = models.CharField(max_length=1, choices=GOAL_FREQUENCY, default=MONTHLY, editable=False)
    def __str__(self) -> str:
        return self.name
        
class Budget(models.Model):
    goal = models.FloatField()
    period = models.IntegerField()
    status = models.CharField(max_length=1, choices=BUDGET_STATUS, default=OPEN, editable=False)
    def __str__(self) -> str:
        return f'{str(self.period)} - {self.status}'
        
class Invite(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(max_length=1000)
    accepted = models.BooleanField(editable=False, default=False)
        
    def accept(self, user):
        group = self.group
        group.members.add(user)
        self.accepted = True
        self.save()
        
    @property
    def link(self):
        token = jwt.encode(
            {
                "exp": timezone.now() + timedelta(days=1),
                "id": self.pk
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        return f"{reverse('finance:invite_acception')}?t={token}"
    
    def send(self, request):
        print('Sending email')

        template_html = 'email/invitation.html'
        template_text = 'email/invitation.txt'

        text = get_template(template_text)
        html = get_template(template_html)

        site = f"{request.scheme}://{request.get_host()}"

        full_link = site + self.link

        d = {
            'site': site,
            'link': full_link
        }

        subject, from_email, to = 'Invite', settings.EMAIL_HOST_USER, self.email
        msg = EmailMultiAlternatives(
            subject=subject, 
            body=text.render(d), 
            from_email=from_email, 
            to=[to])
        msg.attach_alternative(html.render(d), "text/html")
        msg.send(fail_silently = False)
        
    def __str__(self) -> str:
        return f'{str(self.group)} -> {self.email}'

class Notification(models.Model):
    title = models.CharField(max_length=50)
    message = models.CharField(max_length=255)
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True, default=None)
    to = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(blank=True, null=True, default=None)
    action = models.CharField(max_length=1000)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title

    @property
    def read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = timezone.now()
        self.save()

    def set_icon_by_markup(self, markup):
        self.icon = Icon.objects.filter(markup=markup).first()
        self.save()