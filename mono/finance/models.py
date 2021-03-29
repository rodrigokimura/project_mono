from calendar import weekday
from django.conf import settings
from django.db import models
from django.db.models import F, Q, Sum, Value as V
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.template.loader import get_template
from datetime import date, datetime, timedelta
import jwt
import pytz
import stripe
from dateutil.relativedelta import relativedelta

User = get_user_model()

class Transaction(models.Model):
    """Stores financial transactions."""
    description = models.CharField(max_length=50, null=False, blank=False, 
        verbose_name=_("description"), 
        help_text="A short description, so that the user can identify the transaction.")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, 
        verbose_name=_("created by"), 
        help_text="Identifies how created the transaction.")
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    timestamp = models.DateTimeField(_("timestamp"), default=timezone.now, 
        help_text="Timestamp when transaction occurred. User defined.")
    ammount = models.FloatField(_("ammount"), help_text="Ammount related to the transaction. Absolute value, no positive/negative signs.")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=False, verbose_name=_("category"))
    account = models.ForeignKey('Account', on_delete=models.CASCADE, verbose_name=_("account"))
    active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
    
    @property
    def type(self):
        """Gets the type of transaction (Expense /Income) from :model:`finance.Category` type."""
        return self.category.type
        
    @property
    def signed_ammount(self):
        """Same as ammount, but with positive/negative sign, depending on :model:`finance.Category` type."""
        sign = 1
        if self.category.type == 'EXP':
            sign = -1
        return self.ammount*sign
        
    def __str__(self) -> str:
        return self.description

class Icon(models.Model):
    markup = models.CharField(max_length=50, unique=True)
    def __str__(self) -> str:
        return self.markup
    class Meta:
        verbose_name = _("icon")
        verbose_name_plural = _("icons")

class Category(models.Model):
    INCOME = 'INC'
    EXPENSE = 'EXP'
    TRANSACTION_TYPES = [
        (INCOME, _('Income')),
        (EXPENSE, _('Expense')),
    ]
    DEFAULT = 'DEF'
    TRANSFER = 'TRF'
    ADJUSTMENT = 'ADJ'
    INTERNAL_TYPES = [
        (DEFAULT, 'Default'),
        (TRANSFER, 'Transfer'),
        (ADJUSTMENT, 'Balance adjustment'),
    ]
    TRANSFER_NAME = 'Transfer'
    ADJUSTMENT_NAME = 'Balance adjustment'
    
    INITIAL_CATEGORIES = [
        ['Health', 'EXP', 'heartbeat'], 
        ['Shopping', 'EXP', 'cart'], 
        ['Education', 'EXP', 'university'],
        ['Transportation', 'EXP', 'car'],
        ['Trips', 'EXP', 'plane'],
        ['Leisure', 'EXP', 'gamepad'],
        ['Groceries', 'EXP', 'shopping basket'],
        ['Salary', 'INC', 'money bill alternate outline'],
    ]
    SPECIAL_CATEGORIES = [
        [TRANSFER_NAME, 'INC', 'money bill alternate outline', TRANSFER],
        [TRANSFER_NAME, 'EXP', 'money bill alternate outline', TRANSFER],
        [ADJUSTMENT_NAME, 'INC', 'money bill alternate outline', ADJUSTMENT],
        [ADJUSTMENT_NAME, 'EXP', 'money bill alternate outline', ADJUSTMENT],
    ]

    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, default=EXPENSE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True, default=None)
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True)
    internal_type = models.CharField(max_length=3, choices=INTERNAL_TYPES, default=DEFAULT)
    active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        
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
            type = Category.EXPENSE
        elif diff > 0:
            type = Category.INCOME
        else:
            return
        
        qs = Category.objects.filter(
            created_by = user,
            type = type,
            internal_type = Category.ADJUSTMENT
        )
        if qs.exists():
            adjustment_category = qs.first()
        else:
            adjustment_category = Category.objects.create(
                name = Category.ADJUSTMENT_NAME,
                created_by = user,
                type = type,
                internal_type = Category.ADJUSTMENT
            )
        transaction = Transaction(ammount=abs(diff))
        transaction.category = adjustment_category
        transaction.description = "Balance adjustment"
        transaction.account = self
        transaction.created_by = user
        transaction.save()
        
    def remove_group(self):
        self.group = None
        self.save()
        
    def __str__(self) -> str:
        return self.name

class Goal(models.Model):
    WEEKLY = 'W'
    MONTHLY = 'M'
    YEARLY = 'Y'
    GOAL_FREQUENCY = [
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    ]
    CONSTANT = 'C'
    LINEAR = 'L'
    PROGRESSION_MODES = [
        (CONSTANT, 'Constant'),
        (LINEAR, 'Linear'),
    ]
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
        
class BudgetConfiguration(models.Model):
    WEEKLY = 'W'
    MONTHLY = 'M'
    YEARLY = 'Y'
    FREQUENCY = [
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    ammount = models.FloatField()
    start_date = models.IntegerField()
    frequency = models.CharField(max_length=1, choices=FREQUENCY, default=MONTHLY)
    accounts = models.ManyToManyField(Account)
    categories = models.ManyToManyField(Category)
    active = models.BooleanField(default=True)

    def schedule_dates(self, **kwargs):
        reference_date = kwargs["reference_date"]
        if self.frequency == self.WEEKLY:
            current_week = int(kwargs["reference_date"].strftime("%U"))
            start_date = timezone.make_aware(
                datetime.strptime(f"{reference_date.year}-{current_week}-{self.start_date}","%Y-%U-%w"),
                pytz.timezone(settings.STRIPE_TIMEZONE)
            )
            delta = relativedelta(weeks=1)
        elif self.frequency == self.MONTHLY:
            start_date = timezone.make_aware(
                datetime(reference_date.year, reference_date.month - 1, self.start_date),
                pytz.timezone(settings.STRIPE_TIMEZONE)
            )
            delta = relativedelta(months=1)
        elif self.frequency == self.YEARLY:
            start_date = timezone.make_aware(
                datetime(reference_date.year, 1, self.start_date),
                pytz.timezone(settings.STRIPE_TIMEZONE)
            )
            delta = relativedelta(years=1)
        end_date = start_date + delta + relativedelta(days=-1)
        return { "start_date": start_date, "end_date": end_date }

    @property
    def next_schedule_start_date(self):
        dates = self.schedule_dates(reference_date = timezone.now())
        if Budget.objects.filter(configuration = self, start_date = dates["start_date"]).exists():
            return dates["end_date"] + relativedelta(days=1)
        else:
            return dates["start_date"]
    
    @property
    def verbose_interval(self):
        weekdays = [
            _('Sunday'),
            _('Monday'),
            _('Tuesday'),
            _('Wednesday'),
            _('Thursday'),
            _('Friday'),
            _('Saturday'),
        ]
        if self.frequency == self.WEEKLY:
            return _('Every %(d)s of each week.') % {'d': weekdays[self.start_date]}
        elif self.frequency == self.MONTHLY:
            return _('Every day %(d)s of each month.') % {'d': self.start_date}
        elif self.frequency == self.YEARLY:
            return _('Every day %(d)s of each year.') % {'d': self.start_date}

    def create(self):
        dates = self.schedule_dates(reference_date = timezone.now() + timedelta(1))
        if not Budget.objects.filter(configuration = self, start_date = dates["start_date"]).exists():
            budget = Budget(
                created_by = self.created_by,
                ammount = self.ammount,
                start_date = dates["start_date"],
                end_date = dates["end_date"],
                configuration = self,
            )
            budget.save()
            budget.accounts.set(self.accounts.all())
            budget.categories.set(self.categories.all())
            budget.save()

class Budget(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    ammount = models.FloatField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    accounts = models.ManyToManyField(Account)
    categories = models.ManyToManyField(Category)
    configuration = models.ForeignKey(BudgetConfiguration, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self) -> str:
        return f'{str(self.configuration)} - {self.ammount}'
    
    @property
    def open(self):
        return self.end_date >= timezone.now().date()

    @property
    def time_spent(self):
        return (timezone.now().date() - self.start_date).days

    @property
    def time_total(self):
        return (self.end_date - self.start_date).days

    @property
    def time_progress(self):
        if self.open:
            try:
                progress = (timezone.now().date() - self.start_date)/(self.end_date - self.start_date)
            except ZeroDivisionError:
                progress = 0
        else: 
            progress = 1
        return progress


    @property
    def spent_queryset(self):
        return Transaction.objects.filter(
            account__in=self.accounts.all(),
            category__in=self.categories.all(),
            timestamp__date__gte=self.start_date,
            timestamp__date__lt=self.end_date,
        )

    @property
    def ammount_spent(self):
        return self.spent_queryset.aggregate(sum=Coalesce(Sum("ammount"), V(0)))['sum']

    @property
    def ammount_progress(self):
        try: 
            progress = self.ammount_spent / self.ammount
        except ZeroDivisionError:
            progress = 0
        return progress
    
    @property
    def status(self):
        threshold = (.9 * self.ammount)
        if self.ammount_spent < threshold:
            status = 'success'
        elif threshold <= self.ammount_spent < self.ammount_spent:
            status = 'warning'
        else:
            status = 'error'
        return status

    @property
    def progress_bar_color(self):
        if self.ammount_progress < .6:
            color = 'green'
        elif .6 <= self.ammount_progress < .8:
            color = 'olive'
        elif .8 <= self.ammount_progress < .9:
            color = 'yellow'
        elif .9 <= self.ammount_progress < .95:
            color = 'orange'
        else:
            color = 'red'
        return color

        
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
        return f"{reverse('finance:invite_acceptance')}?t={token}"
    
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

class Configuration(models.Model):

    HOME = 'HOM'
    ACCOUNTS = 'ACC'
    TRANSACTIONS = 'TRN'
    GROUPS = 'GRP'
    CATEGORIES = 'CTG'
    GOALS = 'GOL'
    PAGES = [
        (HOME, 'Home'),
        (ACCOUNTS, 'Accounts'),
        (TRANSACTIONS, 'Transactions'),
        (GROUPS, 'Groups'),
        (CATEGORIES, 'Categories'),
        (GOALS, 'Goals'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    main_page = models.CharField(max_length=3, choices=PAGES, default=HOME)

    def __str__(self) -> str:
        return f'Config for {self.user}'

class Plan(models.Model):
    """
    Stores data about the plans user can subscribve to. 
    This models has data used to populate the checkout page.
    Those are related to Stripe products."""

    FREE = 'FR'
    LIFETIME = 'LT'
    DEFAULT = 'DF'
    RECOMMENDED = 'RC'

    TYPE_CHOICES = [
        (FREE,          _('Free')),
        (LIFETIME,      _('Lifetime')),
        (DEFAULT,       _('Default')),
        (RECOMMENDED,   _('Recommended')),
    ]

    product_id = models.CharField(max_length=100, help_text="Stores the stripe unique identifiers")
    name = models.CharField(max_length=100, help_text="Display name used on the template")
    description = models.TextField(max_length=500, help_text="Description text used on the template")
    icon = models.ForeignKey(Icon, null=True, blank=True, default=None, on_delete=models.SET_NULL, help_text="Icon rendered in the template")
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, 
        help_text="Used to customize the template based on this field. For instance, the basic plan will be muted and the recommended one is highlighted.")
    order = models.IntegerField(unique=True, help_text="Used to sort plans on the template.")
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["order"]

class Feature(models.Model):
    """
    Stores features related to the plans user can subscribve to. 
    This models is used to populate the checkout page.
    Those are related to plans that are related to Stripe products."""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, null=True, blank=True, default=None, on_delete=models.SET_NULL, help_text="Icon rendered in the template")
    short_description = models.CharField(max_length=30)
    full_description = models.TextField(max_length=200)
    internal_description = models.TextField(max_length=1000, null=True, blank=True, default=None, help_text="This is used by staff and is not displayed to user in the template.")
    display = models.BooleanField(help_text="Controls wether feature is shown on the template", default=True)

    def __str__(self) -> str:
        return f"{self.plan.name} - {self.short_description}"

class Subscription(models.Model):
    """
    Stores subscriptions made by users. This is used to provide plan features and limitations to user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancel_at = models.DateTimeField(null=True, blank=True)
    event_id = models.CharField(max_length=100)

    @property
    def status(self):
        if self.cancel_at is None:
            status = "active"
        elif self.cancel_at > timezone.now():
            status = "pending"
        elif self.cancel_at <= timezone.now():
            status = "error"
        return status

    def cancel_at_period_end(self):
        try:
            # Update Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.list(email=self.user.email).data[0]
            subscription = stripe.Subscription.list(customer=customer.id).data[0]
            subscription = stripe.Subscription.modify(subscription.id, cancel_at_period_end=True)

            # Update model
            self.cancel_at = timezone.make_aware(
                datetime.fromtimestamp(subscription.cancel_at),
                pytz.timezone(settings.STRIPE_TIMEZONE)
            )
            self.save()
            return (True, "Your subscription has been scheduled to be cancelled at the end of your renewal date.")
        except Exception as e:
            return (False, e)
    
    def abort_cancellation(self):
        if self.cancel_at is not None:
            # Update Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.list(email=self.user.email).data[0]
            subscription = stripe.Subscription.list(customer=customer.id).data[0]
            subscription = stripe.Subscription.modify(subscription.id, cancel_at_period_end=False)

            # Update model
            self.cancel_at = None
            self.save()

    # def cancel_now(self):
    #     self.cancel_at = None
    #     self.plan = Plan.objects.get(type=Plan.FREE)
    #     self.save()

