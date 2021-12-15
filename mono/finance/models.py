from datetime import datetime, timedelta

import jwt
import pytz
import stripe
from accounts.models import Notification
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import FloatField, Q, Sum
from django.db.models.aggregates import Avg, Count
from django.db.models.expressions import F, Func, Value as V
from django.db.models.functions import Coalesce
from django.db.models.functions.datetime import (
    TruncMonth, TruncWeek, TruncYear,
)
from django.db.models.query import QuerySet
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from multiselectfield import MultiSelectField

User = get_user_model()


class Transaction(models.Model):
    """Stores financial transactions."""
    description = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name=_("description"),
        help_text="A short description, so that the user can identify the transaction.")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name=_("created by"),
        help_text="Identifies who created the transaction.")
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True)
    timestamp = models.DateTimeField(
        _("timestamp"), default=timezone.now,
        help_text="Timestamp when transaction occurred. User defined.")
    amount = models.FloatField(
        _("amount"),
        help_text="Amount related to the transaction. Absolute value, no positive/negative signs.")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=False, verbose_name=_("category"))
    account = models.ForeignKey('Account', on_delete=models.CASCADE, verbose_name=_("account"))
    active = models.BooleanField(_("active"), default=True)
    recurrent = models.ForeignKey('RecurrentTransaction', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    installment = models.ForeignKey('Installment', verbose_name=_("installment"), on_delete=models.CASCADE, null=True, blank=True, default=None)
    transference = models.ForeignKey('Transference', verbose_name=_("installment"), on_delete=models.CASCADE, null=True, blank=True, default=None)

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")

    @property
    def type(self):
        """Gets the type of transaction (Expense /Income) from :model:`finance.Category` type."""
        return self.category.type

    @property
    def signed_amount(self):
        """Same as amount, but with positive/negative sign, depending on :model:`finance.Category` type."""
        sign = 1
        if self.category.type == 'EXP':
            sign = -1
        return self.amount * sign

    def round_amount(self):
        self.amount = round(float(self.amount), 2)

    def __str__(self) -> str:
        return self.description


class RecurrentTransaction(models.Model):
    WEEKLY = 'W'
    MONTHLY = 'M'
    YEARLY = 'Y'
    FREQUENCY = [
        (WEEKLY, _('Weekly')),
        (MONTHLY, _('Monthly')),
        (YEARLY, _('Yearly')),
    ]
    description = models.CharField(max_length=50, null=False, blank=False,
                                   verbose_name=_("description"),
                                   help_text="A short description, so that the user can identify the transaction.")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   verbose_name=_("created by"),
                                   help_text="Identifies who created the transaction.")
    timestamp = models.DateTimeField(_("timestamp"), default=timezone.now,
                                     help_text="Timestamp when transaction occurred. User defined.")
    amount = models.FloatField(_("amount"), help_text="Amount related to the transaction. Absolute value, no positive/negative signs.")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=False, verbose_name=_("category"))
    account = models.ForeignKey('Account', on_delete=models.CASCADE, verbose_name=_("account"))
    active = models.BooleanField(_("active"), default=True)
    frequency = models.CharField(_("frequency"), max_length=1, choices=FREQUENCY, default=MONTHLY)

    def is_schedule_date(self, reference_date):
        if reference_date < self.timestamp.date():
            return False
        elif reference_date == self.timestamp.date():
            return True
        else:

            if self.frequency == self.WEEKLY:
                return reference_date.weekday() == self.timestamp.weekday()
            elif self.frequency == self.MONTHLY:
                return reference_date.day == self.timestamp.day
            elif self.frequency == self.YEARLY:
                return reference_date.day == self.timestamp.day and reference_date.month == self.timestamp.month

    @property
    def type(self):
        """Gets the type of transaction (Expense /Income) from :model:`finance.Category` type."""
        return self.category.type

    @property
    def verbose_interval(self):
        weekdays = [
            _('Monday'),
            _('Tuesday'),
            _('Wednesday'),
            _('Thursday'),
            _('Friday'),
            _('Saturday'),
            _('Sunday'),
        ]
        months = [
            _('January'),
            _('February'),
            _('March'),
            _('April'),
            _('May'),
            _('June'),
            _('July'),
            _('August'),
            _('September'),
            _('October'),
            _('November'),
            _('December'),
        ]
        if self.frequency == self.WEEKLY:
            return _('Every %(d)s of each week.') % {'d': weekdays[self.timestamp.weekday()]}
        elif self.frequency == self.MONTHLY:
            return _('Every day %(d)s of each month.') % {'d': self.timestamp.day}
        elif self.frequency == self.YEARLY:
            return _('Every day %(d)s of %(m)s of each year.') % {'d': self.timestamp.day, 'm': months[self.timestamp.month]}

    def create_transaction(self):
        reference_date = (timezone.now() + timedelta(1)).date()
        if not Transaction.objects.filter(recurrent=self, timestamp__date=reference_date).exists() and self.is_schedule_date(reference_date):
            transaction = Transaction(
                description=self.description,
                created_by=self.created_by,
                timestamp=datetime.combine(reference_date, datetime.min.time()),
                amount=self.amount,
                category=self.category,
                account=self.account,
                recurrent=self,
            )
            transaction.save()
            Notification.objects.create(
                title="Group invitation",
                message="A transaction was created",
                to=self.created_by,
                icon="exclamation",
                action_url=reverse("finance:groups"),
            )

    class Meta:
        verbose_name = _("recurrent transaction")
        verbose_name_plural = _("recurrent transactions")


class Installment(models.Model):
    FIRST = 'F'
    LAST = 'L'
    HANDLE_REMAINDER = [
        (FIRST, _('Add to first transaction')),
        (LAST, _('Add to last transaction')),
    ]
    months = models.IntegerField(_("months"), default=12)
    description = models.CharField(_("description"), max_length=50, null=False, blank=False,
                                   help_text="A short description, so that the user can identify the transaction.")
    created_by = models.ForeignKey(User, verbose_name=_("created by"), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(_("timestamp"), default=timezone.now,
                                     help_text="Timestamp when transaction occurred. User defined.")
    total_amount = models.FloatField(_("total amount"), help_text="Amount related to the transaction. Absolute value, no positive/negative signs.")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=False, verbose_name=_("category"))
    account = models.ForeignKey('Account', on_delete=models.CASCADE, verbose_name=_("account"))
    handle_remainder = models.CharField(_("handle remainder"), max_length=1, choices=HANDLE_REMAINDER, default=FIRST)

    def create_transactions(self):
        if self.id is None:
            self.save()
        decimals = 2
        remainder = round(((self.total_amount * 10 ** decimals) % self.months) / 10 ** decimals, decimals)
        amount = round((self.total_amount - remainder) / self.months, decimals)

        if self.handle_remainder == self.FIRST:
            i_to_add_remainder = 0
        elif self.handle_remainder == self.FIRST:
            i_to_add_remainder = self.months - 1

        for i in range(self.months):
            if i == i_to_add_remainder:
                final_amount = amount + remainder
            else:
                final_amount = amount
            Transaction.objects.create(
                description=f'{self.description} - {i + 1}/{self.months}',
                created_by=self.created_by,
                timestamp=self.timestamp + relativedelta(months=i),
                amount=final_amount,
                category=self.category,
                account=self.account,
                installment=self,
            )

    class Meta:
        verbose_name = _("installment")
        verbose_name_plural = _("installments")


class Transference(models.Model):
    """Stores couples of transactions; one income and one expense."""
    description = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        default=_("Transfer"),
        verbose_name=_("description"),
        help_text="A short description, so that the user can identify the transaction.")
    from_account = models.ForeignKey(
        "Account",
        verbose_name=_("from account"),
        on_delete=models.CASCADE,
        related_name="expense_transferences",
        help_text="Source account in which an expense will be stored.")
    to_account = models.ForeignKey(
        "Account",
        verbose_name=_("to account"),
        on_delete=models.CASCADE,
        related_name="income_transferences",
        help_text="Destination account in which an income will be stored.")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("created by"),
        help_text="Identifies who created the transaction.")
    timestamp = models.DateTimeField(
        _("timestamp"), default=timezone.now,
        help_text="Timestamp when transaction occurred. User defined.")
    amount = models.FloatField(
        _("amount"),
        help_text="Amount related to the transaction. Absolute value, no positive/negative signs.")

    def create_transactions(self):
        """Creates a pair of transactions: expense and income."""
        if not Transaction.objects.filter(transference=self.id).exists():
            Transaction.objects.create(
                description=self.description,
                account=self.from_account,
                created_by=self.created_by,
                timestamp=self.timestamp,
                amount=self.amount,
                transference=self,
                category=Category.objects.filter(
                    created_by=self.created_by,
                    internal_type=Category.TRANSFER,
                    type=Category.EXPENSE,
                ).last(),
            )
            Transaction.objects.create(
                description=self.description,
                account=self.to_account,
                created_by=self.created_by,
                timestamp=self.timestamp,
                amount=self.amount,
                transference=self,
                category=Category.objects.filter(
                    created_by=self.created_by,
                    internal_type=Category.TRANSFER,
                    type=Category.INCOME,
                ).last(),
            )


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
        (EXPENSE, _('Expense')),
        (INCOME, _('Income')),
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
        return self.is_group_defined or self.is_user_defined


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

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")


class Account(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="created_accountset", null=True)
    owned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_accountset")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    initial_balance = models.FloatField(default=0)
    credit_card = models.BooleanField(default=False)
    settlement_date = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(28),
        ]
    )
    due_date = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(28),
        ]
    )

    @property
    def is_shared(self):
        return self.group is not None

    @property
    def current_balance(self):
        decimals = 2
        qs = self.transaction_set.all()
        income_sum = Coalesce(
            Sum(
                'amount',
                filter=Q(category__type='INC'),
                output_field=FloatField()
            ),
            V(0),
            output_field=FloatField()
        )
        expense_sum = Coalesce(
            Sum(
                'amount',
                filter=Q(category__type='EXP'),
                output_field=FloatField()
            ),
            V(0),
            output_field=FloatField()
        )
        balance = qs.aggregate(
            balance=income_sum - expense_sum
        )['balance']
        sum = self.initial_balance + balance
        return round(sum, decimals)

    @property
    def total_transactions(self):
        qs = Transaction.objects.filter(account=self.pk)
        return qs.count()

    def _get_coalesce_sum(self):
        return Coalesce(
            Sum(
                'amount',
                output_field=FloatField()
            ),
            V(0),
            output_field=FloatField()
        )

    def _get_credit_card_transactions(self, year, month):
        if not self.credit_card:
            raise Exception('Account is not of type credit card.')
        qs = self.transaction_set.all()
        if self.settlement_date >= 15:
            month -= 1
        range_start = datetime(
            year,
            month,
            self.settlement_date,
        )
        if month == 12:
            range_end = datetime(
                year + 1,
                1,
                self.due_date,
            )
        else:
            range_end = datetime(
                year,
                month + 1,
                self.settlement_date,
            )
        qs = qs.filter(
            timestamp__range=[range_start, range_end],
        )
        return qs

    def get_credit_card_expenses(self, year, month):
        qs = self._get_credit_card_transactions(year, month)
        qs = qs.filter(category__type='EXP')
        coalesce_sum = self._get_coalesce_sum()
        return qs.aggregate(
            sum=-coalesce_sum
        )['sum']

    def get_credit_card_adjustments(self, year, month):
        qs = self._get_credit_card_transactions(year, month)
        qs = qs.filter(category__type='INC').filter(category__internal_type='ADJ')
        coalesce_sum = self._get_coalesce_sum()
        return qs.aggregate(
            sum=coalesce_sum
        )['sum']

    def get_credit_card_payments(self, year, month):
        qs = self._get_credit_card_transactions(year, month)
        qs = qs.filter(category__type='INC')
        coalesce_sum = self._get_coalesce_sum()
        return qs.aggregate(
            sum=coalesce_sum
        )['sum']

    def is_invoice_paid(self, year, month):
        payments = self.get_credit_card_payments(year, month)
        expenses = self.get_credit_card_expenses(year, month)
        return round(payments, 2) >= -round(expenses, 2)

    @property
    def current_invoice(self):
        now = timezone.now()
        exp = self.get_credit_card_expenses(now.year, now.month)
        inc = self.get_credit_card_adjustments(now.year, now.month)
        return round(exp, 2) + round(inc, 2)

    @property
    def current_invoice_is_paid(self):
        now = timezone.now()
        return self.is_invoice_paid(now.year, now.month)

    @property
    def last_closed_invoice(self):
        now = timezone.now()
        month = now.month
        if self.settlement_date >= 15:
            month -= 1
        if now.day >= self.settlement_date:
            month -= 1
        return self.get_credit_card_expenses(now.year, month)

    @property
    def last_closed_invoice_is_paid(self):
        now = timezone.now()
        month = now.month
        if self.settlement_date >= 15:
            month -= 1
        if now.day >= self.settlement_date:
            month -= 1
        return self.is_invoice_paid(now.year, month)

    def adjust_balance(self, target, user):
        diff = target - self.current_balance
        if diff < 0:
            type = Category.EXPENSE
        elif diff > 0:
            type = Category.INCOME
        else:
            return

        qs = Category.objects.filter(
            created_by=user,
            type=type,
            internal_type=Category.ADJUSTMENT
        )
        if qs.exists():
            adjustment_category = qs.first()
        else:
            adjustment_category = Category.objects.create(
                name=Category.ADJUSTMENT_NAME,
                created_by=user,
                type=type,
                internal_type=Category.ADJUSTMENT
            )
        transaction = Transaction(amount=abs(round(diff, 2)))
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

    class Meta:
        verbose_name = _("account")
        verbose_name_plural = _("accounts")


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
    target_amount = models.FloatField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    progression_mode = models.CharField(max_length=1, choices=PROGRESSION_MODES, default=CONSTANT)
    frequency = models.CharField(max_length=1, choices=GOAL_FREQUENCY, default=MONTHLY, editable=False)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("goal")
        verbose_name_plural = _("goals")


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
    amount = models.FloatField()
    start_date = models.DateField()
    frequency = models.CharField(max_length=1, choices=FREQUENCY, default=MONTHLY)
    accounts = models.ManyToManyField(Account)
    categories = models.ManyToManyField(Category)
    all_accounts = models.BooleanField(_("all accounts"), default=False)
    all_categories = models.BooleanField(_("all categories"), default=False)
    active = models.BooleanField(default=True)

    def is_schedule_date(self, reference_date):
        if reference_date < self.start_date:
            return False
        elif reference_date == self.start_date:
            return True
        else:

            if self.frequency == self.WEEKLY:
                return reference_date.weekday() == self.start_date.weekday()
            elif self.frequency == self.MONTHLY:
                return reference_date.day == self.start_date.day
            elif self.frequency == self.YEARLY:
                return reference_date.day == self.start_date.day and reference_date.month == self.start_date.month

    @property
    def verbose_interval(self):
        weekdays = [
            _('Monday'),
            _('Tuesday'),
            _('Wednesday'),
            _('Thursday'),
            _('Friday'),
            _('Saturday'),
            _('Sunday'),
        ]
        months = [
            _('January'),
            _('February'),
            _('March'),
            _('April'),
            _('May'),
            _('June'),
            _('July'),
            _('August'),
            _('September'),
            _('October'),
            _('November'),
            _('December'),
        ]
        if self.frequency == self.WEEKLY:
            return _('Every %(d)s of each week.') % {'d': weekdays[self.start_date.weekday()]}
        elif self.frequency == self.MONTHLY:
            return _('Every day %(d)s of each month.') % {'d': self.start_date.day}
        elif self.frequency == self.YEARLY:
            return _('Every day %(d)s of %(m)s of each year.') % {'d': self.start_date.day, 'm': months[self.start_date.month]}

    def create_budget(self):
        reference_date = (timezone.now() + timedelta(1)).date()

        if self.frequency == self.WEEKLY:
            delta = relativedelta(weeks=1)
        elif self.frequency == self.MONTHLY:
            delta = relativedelta(months=1)
        elif self.frequency == self.YEARLY:
            delta = relativedelta(years=1)

        if not Budget.objects.filter(configuration=self, start_date=reference_date).exists() and self.is_schedule_date(reference_date):
            budget = Budget(
                created_by=self.created_by,
                amount=self.amount,
                start_date=reference_date,
                end_date=reference_date + delta + relativedelta(days=-1),
                configuration=self,
                all_accounts=self.all_accounts,
                all_categories=self.all_categories,
            )
            budget.save()
            budget.accounts.set(self.accounts.all())
            budget.categories.set(self.categories.all())
            budget.save()

    class Meta:
        verbose_name = _("budget configuration")
        verbose_name_plural = _("budget configurations")


class Budget(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(_("amount"))
    start_date = models.DateField(_("start date"), default=timezone.now)
    end_date = models.DateField(_("end date"))
    accounts = models.ManyToManyField(Account, verbose_name=_("accounts"))
    categories = models.ManyToManyField(Category, verbose_name=_("categories"))
    all_accounts = models.BooleanField(_("all accounts"), default=False)
    all_categories = models.BooleanField(_("all categories"), default=False)
    configuration = models.ForeignKey(BudgetConfiguration, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("configuration"))

    class Meta:
        verbose_name = _("budget")
        verbose_name_plural = _("budgets")

    def __str__(self) -> str:
        return f'{str(self.configuration)} - {self.amount}'

    @property
    def open(self):
        return self.end_date >= timezone.now().date()

    @property
    def time_spent(self):
        if self.end_date < timezone.now().date():
            return (self.end_date - self.start_date).days + 1
        else:
            return (timezone.now().date() - self.start_date).days

    @property
    def time_total(self):
        return (self.end_date - self.start_date).days + 1

    @property
    def time_progress(self):
        if self.open:
            try:
                progress = (timezone.now().date() - self.start_date) / (self.end_date - self.start_date)
            except ZeroDivisionError:
                progress = 0
        else:
            progress = 1
        return progress

    @property
    def spent_queryset(self):

        if self.all_accounts:
            owned_accounts = Account.objects.filter(owned_by=self.created_by)
            shared_accounts = Account.objects.filter(group__members=self.created_by)
            accounts = (owned_accounts | shared_accounts).distinct()
        else:
            accounts = self.accounts.all()

        if self.all_categories:
            user_categories = Category.objects.filter(
                created_by=self.created_by,
                type=Category.EXPENSE,
                internal_type=Category.DEFAULT
            )
            group_categories = Category.objects.filter(
                group__members=self.created_by,
                type=Category.EXPENSE,
                internal_type=Category.DEFAULT
            )
            categories = (user_categories | group_categories).distinct()
        else:
            categories = self.categories.all()

        return Transaction.objects.filter(
            account__in=accounts,
            category__in=categories,
            timestamp__date__gte=self.start_date,
            timestamp__date__lte=self.end_date,
        )

    @property
    def amount_spent(self):
        return self.spent_queryset.aggregate(sum=Coalesce(Sum("amount"), V(0), output_field=FloatField()))['sum']

    @property
    def amount_progress(self):
        try:
            progress = self.amount_spent / self.amount
        except ZeroDivisionError:
            progress = 0
        return progress

    @property
    def status(self):
        threshold = (.9 * self.amount)
        if self.amount_spent < threshold:
            status = 'success'
        elif threshold <= self.amount_spent < self.amount_spent:
            status = 'warning'
        else:
            status = 'error'
        return status

    @property
    def progress_bar_color(self):
        if self.amount_progress < .6:
            color = 'green'
        elif .6 <= self.amount_progress < .8:
            color = 'olive'
        elif .8 <= self.amount_progress < .9:
            color = 'yellow'
        elif .9 <= self.amount_progress < .95:
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

    class Meta:
        verbose_name = _("invite")
        verbose_name_plural = _("invites")

    def accept(self, user):
        group = self.group
        group.members.add(user)
        self.accepted = True
        self.save()
        Notification.objects.create(
            title="Group invitation",
            message=f"{user} accepted your invite.",
            to=self.created_by,
            icon="exclamation",
            action_url=reverse("finance:groups"),
        )

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

        subject, from_email, to = _('Invite'), settings.EMAIL_HOST_USER, self.email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text.render(d),
            from_email=from_email,
            to=[to])
        msg.attach_alternative(html.render(d), "text/html")
        msg.send(fail_silently=False)
        if User.objects.filter(email=self.email).exists():
            Notification.objects.create(
                title=_("Group invitation"),
                message=_("You were invited to be part of a group."),
                to=User.objects.get(email=self.email),
                icon="exclamation",
                action_url=full_link
            )

    def __str__(self) -> str:
        return f'{str(self.group)} -> {self.email}'


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

    C_OVERVIEW = 1
    C_BALANCE = 2
    C_BUDGETS = 3
    CARDS = [
        (C_OVERVIEW, _('Overview')),
        (C_BALANCE, _('Balance')),
        (C_BUDGETS, _('Budgets')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    main_page = models.CharField(max_length=3, choices=PAGES, default=HOME)
    cards = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text="Used to store comma-separated string of integers \
            corresponding to cards"
    )

    class Meta:
        verbose_name = _("configuration")
        verbose_name_plural = _("configurations")

    def __str__(self) -> str:
        return f'Config for {self.user}'

    @property
    def cards_list(self):
        if self.cards:
            return list(map(int, self.cards.split(',')))
        else:
            return None

    @property
    def decoded_cards(self):
        if self.cards:
            cards_list = []
            for i in self.cards_list:
                cards_list.append([n for v, n in self.CARDS if v == i][0])
            return cards_list
        else:
            return None


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
        (FREE, _('Free')),
        (LIFETIME, _('Lifetime')),
        (DEFAULT, _('Default')),
        (RECOMMENDED, _('Recommended')),
    ]

    product_id = models.CharField(max_length=100, help_text="Stores the stripe unique identifiers")
    name = models.CharField(max_length=100, help_text="Display name used on the template")
    description = models.TextField(max_length=500, help_text="Description text used on the template")
    icon = models.ForeignKey(Icon, null=True, blank=True, default=None, on_delete=models.SET_NULL, help_text="Icon rendered in the template")
    type = models.CharField(max_length=2, choices=TYPE_CHOICES,
                            help_text="Used to customize the template based on this field. For instance, the basic plan will be muted and the recommended one is highlighted.")
    order = models.IntegerField(unique=True, help_text="Used to sort plans on the template.")

    class Meta:
        verbose_name = _("plan")
        verbose_name_plural = _("plans")
        ordering = ["order"]

    def __str__(self) -> str:
        return self.name


class Feature(models.Model):
    """
    Stores features related to the plans user can subscribe to.
    This models is used to populate the checkout page.
    Those are related to plans that are related to Stripe products."""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, null=True, blank=True, default=None, on_delete=models.SET_NULL, help_text="Icon rendered in the template")
    short_description = models.CharField(max_length=30)
    full_description = models.TextField(max_length=200)
    internal_description = models.TextField(max_length=1000, null=True, blank=True, default=None, help_text="This is used by staff and is not displayed to user in the template.")
    display = models.BooleanField(help_text="Controls wether feature is shown on the template", default=True)

    class Meta:
        verbose_name = _("feature")
        verbose_name_plural = _("features")

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

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

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


class Chart(models.Model):
    TYPE_CHOICES = [
        ('bar', _('Bar')),
        ('line', _('Line')),
        ('column', _('Column')),
        ('donut', _('Donut')),
    ]
    METRIC_CHOICES = [
        ('count', _('Count')),
        ('sum', _('Sum')),
        ('avg', _('Average')),
    ]
    FIELD_CHOICES = [
        ('transaction', _('Transaction')),
        ('transference', _('Transference')),
        ('recurrent_transaction', _('Recurrent Transaction')),
        ('installment', _('Installment')),
    ]
    AXIS_CHOICES = [
        ('year', _('Year')),
        ('month', _('Month')),
        ('week', _('Week')),
    ]
    CATEGORY_CHOICES = [
        ('category', _('Category')),
        ('type', _('Type')),
    ]
    FILTER_CHOICES = [
        ('expenses', _('Expenses')),
        ('incomes', _('Incomes')),
        ('balance_adjustments', _('Balance adjustments')),
        ('not_balance_adjustments', _('Not balance adjustments')),
        ('transferences', _('Transferences')),
        ('not_transferences', _('Not transferences')),
        ('current_year', _('Current year')),
        ('past_year', _('Past year')),
        ('current_month', _('Current month')),
        ('past_month', _('Past month')),
    ]
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default='bar')
    metric = models.CharField(max_length=100, choices=METRIC_CHOICES, default='sum')
    field = models.CharField(max_length=100, choices=FIELD_CHOICES, default='transaction')
    axis = models.CharField(max_length=100, choices=AXIS_CHOICES, default='month', null=True, blank=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='category', null=True, blank=True)
    filters = MultiSelectField(choices=FILTER_CHOICES, null=True, blank=True, default=None)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='charts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100, default='Untitled chart')
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['order', 'created_by']

    def __str__(self):
        text = (
            f"{self.get_metric_display()} of {self.get_field_display()}"
        )
        if self.axis:
            text += f" by {self.get_axis_display()}"
        if self.category:
            text += f" grouped by {self.get_category_display()}"
        if self.filters:
            text += f" filtered by {self.get_filters_display()}"
        return text

    def _apply_field(self, user):
        if self.field == 'transaction':
            qs = Transaction.objects.filter(created_by=user)
        elif self.field == 'transference':
            qs = Transference.objects.filter(created_by=user)
        elif self.field == 'recurrent_transaction':
            qs = RecurrentTransaction.objects.filter(created_by=user)
        elif self.field == 'installment':
            qs = Installment.objects.filter(created_by=user)
        else:
            raise NotImplementedError('Field not implemented')
        return qs

    def _apply_filter(self, qs: QuerySet):
        if 'expenses' in self.filters:
            qs = qs.filter(category__type=Category.EXPENSE)
        if 'incomes' in self.filters:
            qs = qs.filter(category__type=Category.INCOME)
        if 'balance_adjustments' in self.filters:
            qs = qs.filter(category__internal_type=Category.ADJUSTMENT)
        if 'not_balance_adjustments' in self.filters:
            qs = qs.exclude(category__internal_type=Category.ADJUSTMENT)
        if 'transferences' in self.filters:
            qs = qs.filter(category__internal_type=Category.TRANSFER)
        if 'not_transferences' in self.filters:
            qs = qs.exclude(category__internal_type=Category.TRANSFER)
        if 'current_year' in self.filters:
            qs = qs.filter(timestamp__year=timezone.now().year)
        if 'past_year' in self.filters:
            qs = qs.filter(timestamp__year=timezone.now().year - 1)
        if 'current_month' in self.filters:
            qs = qs.filter(timestamp__month=timezone.now().month)
        if 'past_month' in self.filters:
            qs = qs.filter(timestamp__month=timezone.now().month - 1)
        return qs

    def _apply_axis(self, qs: QuerySet):
        if self.axis is None:
            return qs.annotate(axis=V("No axis"))

        db_engine = settings.DATABASES["default"]["ENGINE"]

        if self.axis == 'year':
            format = {
                'django.db.backends.mysql': '%Y',
                'django.db.backends.sqlite3': '%Y',
            }
            qs = qs.annotate(date=TruncYear('timestamp'))
        elif self.axis == 'month':
            format = {
                'django.db.backends.mysql': '%Y-%m',
                'django.db.backends.sqlite3': '%Y-%m',
            }
            qs = qs.annotate(date=TruncMonth('timestamp'))
        elif self.axis == 'week':
            format = {
                'django.db.backends.mysql': '%Y-%V',
                'django.db.backends.sqlite3': '%Y-%W',
            }
            qs = qs.annotate(date=TruncWeek('timestamp'))
        else:
            raise NotImplementedError('Axis not implemented')
        if db_engine == "django.db.backends.mysql":
            qs = qs.annotate(
                axis=Func(
                    F('date'),
                    V(format[db_engine]),
                    function='DATE_FORMAT',
                    output_field=models.CharField()
                )
            )
        elif db_engine == "django.db.backends.sqlite3":
            qs = qs.annotate(
                axis=Func(
                    V(format[db_engine]),
                    F('date'),
                    function='strftime',
                    output_field=models.CharField()
                )
            )
        else:
            raise NotImplementedError('Queryset not implemented for this database engine')
        return qs

    def _apply_metric(self, qs: QuerySet):
        if self.metric == 'count':
            qs = qs.annotate(
                metric=Coalesce(
                    Count('amount'),
                    V(0),
                    output_field=models.IntegerField()
                )
            )
        elif self.metric == 'sum':
            qs = qs.annotate(
                metric=Coalesce(
                    Sum('amount'),
                    V(0),
                    output_field=models.FloatField()
                )
            )
        elif self.metric == 'avg':
            qs = qs.annotate(
                metric=Coalesce(
                    Avg('amount'),
                    V(0),
                    output_field=models.FloatField()
                )
            )
        else:
            raise NotImplementedError('Metric not implemented')
        return qs

    def _apply_category(self, qs: QuerySet):
        if self.category is None:
            return qs.annotate(categ=V(f"{self.get_metric_display()} of {self.get_field_display()}"))
        if self.category == 'category':
            qs = qs.annotate(categ=F('category__name'))
        elif self.category == 'type':
            qs = qs.annotate(categ=F('category__type'))
        else:
            raise NotImplementedError('Category not implemented')
        return qs

    def get_queryset(self, user):
        qs = self._apply_field(user)
        qs = self._apply_filter(qs)
        qs = self._apply_axis(qs)
        qs = self._apply_metric(qs)
        qs = self._apply_category(qs)
        qs = qs.values('categ', 'axis', 'metric').order_by('categ', 'axis')
        return qs
