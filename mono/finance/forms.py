"""Finance's forms"""
import logging
from datetime import datetime, timedelta
from random import randint, randrange
from typing import Dict, List

import pytz
from __mono.widgets import (
    ButtonsWidget,
    CalendarWidget,
    IconWidget,
    RadioWidget,
    ToggleWidget,
)
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
from faker import Faker
from faker.providers import lorem

from .models import (
    Account,
    Budget,
    BudgetConfiguration,
    Category,
    Goal,
    Group,
    Icon,
    Installment,
    RecurrentTransaction,
    Transaction,
)
from .widgets import CategoryWidget

User = get_user_model()

logger = logging.getLogger(__name__)


class AccountForm(forms.ModelForm):
    """
    Account form
    """

    error_css_class = "error"
    current_balance = forms.FloatField(
        required=False, label=_("Current balance")
    )
    credit_card = forms.BooleanField(
        required=False,
        label=_("Credit card"),
        widget=ToggleWidget,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"placeholder": _("Description")}
        )
        self.fields["group"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["credit_card"].widget.attrs.update(
            {"class": "ui radio checkbox"}
        )
        if self.instance.pk:
            if self.instance.owned_by != self.request.user:
                self.fields["group"].widget.attrs.update(
                    {"class": "ui disabled dropdown"}
                )

        self.fields["group"].queryset = Group.objects.filter(
            members=self.request.user
        )
        self.fields["initial_balance"].widget.attrs.update(
            {"placeholder": _("Initial balance")}
        )
        if self.instance.pk is None:
            self.fields["current_balance"].widget = forms.HiddenInput()
        else:
            self.fields["current_balance"].widget.attrs.update(
                {
                    "value": self.instance.current_balance,
                    "placeholder": _("Current balance"),
                }
            )

    def clean(self):
        if self.instance.pk is not None:
            if self.instance.owned_by != self.request.user:
                if self.instance.group != self.cleaned_data["group"]:
                    raise ValidationError(
                        _("You don't have permission to change the group.")
                    )
        return self.cleaned_data

    def save(self, *args, **kwargs):
        account = self.instance
        if account.pk is None:
            account.created_by = self.request.user
            account.owned_by = self.request.user
        current_balance = self.cleaned_data["current_balance"]
        if current_balance is not None:
            account.adjust_balance(current_balance, self.request.user)
        return super().save(*args, **kwargs)

    class Meta:
        model = Account
        fields = [
            "name",
            "group",
            "initial_balance",
            "credit_card",
            "settlement_date",
            "due_date",
        ]


class UniversalTransactionForm(forms.Form):
    """
    Transaction,
    Installment,
    Recurrent transaction form
    """

    error_css_class = "error"

    transaction_types = Category.TRANSACTION_TYPES.copy()
    transaction_types.append(("TRF", _("Transfer")))

    type = forms.CharField(
        label=_("Type"),
        widget=ButtonsWidget(choices=transaction_types),
        initial=Category.EXPENSE,
    )
    description = forms.CharField(
        label=_("Description"),
    )
    timestamp = forms.DateTimeField(
        label=_("Timestamp"),
        widget=CalendarWidget,
        initial=timezone.now(),
    )
    account = forms.ModelChoiceField(
        label=_("Account"),
        required=False,
        queryset=Account.objects.all(),
    )
    amount = forms.FloatField(
        label=_("Amount"),
    )
    category = forms.ModelChoiceField(
        label=_("Category"),
        required=False,
        widget=CategoryWidget,
        queryset=Category.objects.all(),
    )
    active = forms.BooleanField(
        label=_("Active"),
        widget=ToggleWidget,
        initial=True,
    )
    frequency = forms.ChoiceField(
        label=_("Frequency"),
        choices=RecurrentTransaction.FREQUENCY,
        initial=RecurrentTransaction.MONTHLY,
    )
    months = forms.IntegerField(
        label=_("Months"),
        initial=12,
    )
    is_recurrent_or_installment = forms.BooleanField(
        label=_("Recurrent or installment?"),
        widget=ToggleWidget,
        initial=False,
        required=False,
    )
    recurrent_or_installment = forms.CharField(
        label=_("Recurrent or installment"),
        required=False,
        widget=RadioWidget(
            choices=[
                ("R", _("Recurrent")),
                ("I", _("Installment")),
            ]
        ),
    )
    handle_remainder = forms.ChoiceField(
        label=_("Handle remainder"),
        choices=Installment.HANDLE_REMAINDER,
        initial=Installment.FIRST,
    )
    # For transference
    from_account = forms.ModelChoiceField(
        label=_("From account"), required=False, queryset=Account.objects.all()
    )
    to_account = forms.ModelChoiceField(
        label=_("To account"), required=False, queryset=Account.objects.all()
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        owned_accounts = Account.objects.filter(owned_by=self.request.user)
        shared_accounts = Account.objects.filter(
            group__members=self.request.user
        )
        self.fields["description"].widget.attrs.update(
            {"placeholder": _("Description")}
        )
        self.fields["amount"].widget.attrs.update({"placeholder": _("Amount")})
        self.fields["category"].widget.queryset = Category.objects.filter(
            created_by=self.request.user, internal_type=Category.DEFAULT
        )
        self.fields["account"].queryset = (
            owned_accounts | shared_accounts
        ).distinct()
        self.fields["from_account"].queryset = (
            owned_accounts | shared_accounts
        ).distinct()
        self.fields["to_account"].queryset = (
            owned_accounts | shared_accounts
        ).distinct()
        self.fields["account"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["from_account"].widget.attrs.update(
            {"class": "ui dropdown"}
        )
        self.fields["to_account"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["frequency"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["recurrent_or_installment"].widget.attrs.update(
            {"class": "ui radio checkbox"}
        )

    def _validate_required_fields(
        self, errors: Dict[str, ValidationError], required_fields: List[str]
    ) -> Dict[str, ValidationError]:
        """
        Validate if fields are missing
        """
        for field in required_fields:
            if field not in self.cleaned_data:
                errors[field] = ValidationError(_("This field is required."))
        return errors

    def clean(self):
        transaction_type = self.cleaned_data["type"]
        errors = {}
        if transaction_type == "TRF":
            # if Transfer, from and to accounts are required
            errors = self._validate_required_fields(
                errors, ["from_account", "to_account"]
            )
        elif self.cleaned_data["is_recurrent_or_installment"]:
            # if Recurrent, Installment or Transaction, account and category are required
            errors = self._validate_required_fields(
                errors, ["account", "category"]
            )
            if self.cleaned_data.get("recurrent_or_installment") == "R":
                errors = self._validate_required_fields(errors, ["frequency"])
            elif self.cleaned_data.get("recurrent_or_installment") == "I":
                errors = self._validate_required_fields(
                    errors, ["months", "handle_remainder"]
                )
            elif self.cleaned_data.get("recurrent_or_installment") == "":
                errors = self._validate_required_fields(
                    errors, ["recurrent_or_installment"]
                )
        if len(errors) > 0:
            raise ValidationError(errors)


class TransactionForm(forms.ModelForm):
    """
    Transaction form
    """

    error_css_class = "error"

    type = forms.CharField(
        widget=ButtonsWidget(choices=Category.TRANSACTION_TYPES)
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        owned_accounts = Account.objects.filter(owned_by=self.request.user)
        shared_accounts = Account.objects.filter(
            group__members=self.request.user
        )
        self.fields["description"].widget.attrs.update(
            {"placeholder": _("Description")}
        )
        self.fields["amount"].widget.attrs.update({"placeholder": _("Amount")})
        self.fields["category"].widget.queryset = Category.objects.filter(
            created_by=self.request.user, internal_type=Category.DEFAULT
        )
        self.fields["account"].queryset = (
            owned_accounts | shared_accounts
        ).distinct()
        self.fields["account"].widget.attrs.update({"class": "ui dropdown"})
        if self.instance.pk is not None:
            self.fields["type"].initial = self.instance.category.type
        else:
            self.fields["type"].initial = Category.EXPENSE

    class Meta:
        model = Transaction
        fields = [
            "type",
            "description",
            "timestamp",
            "account",
            "amount",
            "category",
            "active",
        ]
        widgets = {
            "category": CategoryWidget,
            "timestamp": CalendarWidget,
            "active": ToggleWidget,
        }

    def save(self, *args, **kwargs):
        category = self.instance
        category.created_by = self.request.user
        category.save()
        return super().save(*args, **kwargs)


class RecurrentTransactionForm(forms.ModelForm):
    """
    Recurrent transaction form
    """

    error_css_class = "error"

    type = forms.CharField(
        widget=ButtonsWidget(choices=Category.TRANSACTION_TYPES)
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        owned_accounts = Account.objects.filter(owned_by=self.request.user)
        shared_accounts = Account.objects.filter(
            group__members=self.request.user
        )
        self.fields["description"].widget.attrs.update(
            {"placeholder": _("Description")}
        )
        self.fields["amount"].widget.attrs.update({"placeholder": _("Amount")})
        self.fields["category"].widget.queryset = Category.objects.filter(
            created_by=self.request.user, internal_type=Category.DEFAULT
        )
        self.fields["account"].queryset = (
            owned_accounts | shared_accounts
        ).distinct()
        self.fields["account"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["frequency"].widget.attrs.update({"class": "ui dropdown"})
        if self.instance.pk is not None:
            self.fields["type"].initial = self.instance.category.type
        else:
            self.fields["type"].initial = Category.EXPENSE

    class Meta:
        model = RecurrentTransaction
        fields = [
            "type",
            "amount",
            "description",
            "account",
            "category",
            "timestamp",
            "active",
            "frequency",
        ]
        widgets = {
            "category": CategoryWidget,
            "timestamp": CalendarWidget,
            "active": ToggleWidget,
        }

    def save(self, *args, **kwargs):
        category = self.instance
        category.created_by = self.request.user
        category.save()
        return super().save(*args, **kwargs)


class InstallmentForm(forms.ModelForm):
    """
    Installment form
    """

    error_css_class = "error"

    type = forms.CharField(
        widget=ButtonsWidget(choices=Category.TRANSACTION_TYPES)
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        owned_accounts = Account.objects.filter(owned_by=self.request.user)
        shared_accounts = Account.objects.filter(
            group__members=self.request.user
        )
        self.fields["description"].widget.attrs.update(
            {"placeholder": _("Description")}
        )
        self.fields["total_amount"].widget.attrs.update(
            {"placeholder": _("Total amount")}
        )
        self.fields["category"].widget.queryset = Category.objects.filter(
            created_by=self.request.user, internal_type=Category.DEFAULT
        )
        self.fields["account"].queryset = (
            owned_accounts | shared_accounts
        ).distinct()
        self.fields["account"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["handle_remainder"].widget.attrs.update(
            {"class": "ui dropdown"}
        )
        if self.instance.pk is not None:
            self.fields["type"].initial = self.instance.category.type
        else:
            self.fields["type"].initial = Category.EXPENSE

    class Meta:
        model = Installment
        fields = [
            "type",
            "total_amount",
            "description",
            "account",
            "category",
            "timestamp",
            "months",
            "handle_remainder",
        ]
        widgets = {
            "category": CategoryWidget,
            "timestamp": CalendarWidget,
        }

    def save(self, *args, **kwargs):
        category = self.instance
        category.created_by = self.request.user
        category.save()
        return super().save(*args, **kwargs)


class GroupForm(forms.ModelForm):
    """
    Group form
    """

    error_css_class = "error"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"placeholder": "Name"})

    class Meta:
        model = Group
        fields = ["name"]

    def save(self, *args, **kwargs):
        user = self.request.user
        if self.instance.id is None:
            self.instance.created_by = user
            self.instance.owned_by = user
        group = self.instance
        group.save()
        group.members.add(user)
        return super().save(*args, **kwargs)


class CategoryForm(forms.ModelForm):
    """
    Category form
    """

    error_css_class = "error"

    class Meta:
        model = Category
        fields = [
            "name",
            "description",
            "type",
            "group",
            "icon",
            "active",
        ]
        widgets = {"icon": IconWidget(entity_type=Icon), "active": ToggleWidget}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"placeholder": "Name"})
        self.fields["description"].widget.attrs.update({"rows": 3})
        self.fields["description"].widget.attrs.update(
            {"placeholder": "Description"}
        )
        self.fields["type"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["group"].widget.attrs.update({"class": "ui dropdown"})

    def save(self, *args, **kwargs):
        category = self.instance
        category.created_by = self.request.user
        category.save()
        return super().save(*args, **kwargs)


class IconForm(forms.ModelForm):
    """
    Icon form
    """

    error_css_class = "error"

    class Meta:
        model = Icon
        fields = ["markup"]

    def save(self, *args, **kwargs):
        icon = self.instance
        icon.markup = icon.markup.lower()
        icon.save()
        return super().save(*args, **kwargs)


class GoalForm(forms.ModelForm):
    """
    Goal form
    """

    error_css_class = "error"

    class Meta:
        model = Goal
        fields = [
            "name",
            "start_date",
            "target_date",
            "target_amount",
            "group",
            "progression_mode",
        ]
        widgets = {
            "start_date": CalendarWidget,
            "target_date": CalendarWidget,
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["start_date"].widget.type = "date"
        self.fields["start_date"].widget.format = "n/d/Y"
        self.fields["target_date"].widget.type = "date"
        self.fields["target_date"].widget.format = "n/d/Y"
        self.fields["name"].widget.attrs.update({"placeholder": "Name"})
        self.fields["group"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["progression_mode"].widget.attrs.update(
            {"class": "ui dropdown"}
        )

    def save(self, *args, **kwargs):
        goal = self.instance
        if goal.id is None:
            goal.created_by = self.request.user
        goal.save()
        return super().save(*args, **kwargs)


class BudgetForm(forms.ModelForm):
    """
    Budget form
    """

    error_css_class = "error"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        shared_accounts = Account.objects.filter(
            group__members=self.request.user
        )
        owned_accounts = Account.objects.filter(
            owned_by=self.request.user, group=None
        )
        self.fields["accounts"].queryset = (
            shared_accounts | owned_accounts
        ).distinct()
        self.fields["accounts"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["start_date"].widget.type = "date"
        self.fields["end_date"].widget.type = "date"
        created_categories = Category.objects.filter(
            created_by=self.request.user,
            internal_type=Category.DEFAULT,
            group=None,
            type=Category.EXPENSE,
        )
        shared_categories = Category.objects.filter(
            group__members=self.request.user, type=Category.EXPENSE
        )
        self.fields["categories"].queryset = (
            shared_categories | created_categories
        ).distinct()
        self.fields["categories"].widget.attrs.update({"class": "ui dropdown"})

    def clean(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")
        if start_date > end_date:
            raise ValidationError(
                _("Your end date must be after your start date.")
            )
        return self.cleaned_data

    def save(self, *args, **kwargs):
        budget = self.instance
        if budget.pk is None:
            budget.created_by = self.request.user
        budget.save()
        return super().save(*args, **kwargs)

    class Meta:
        model = Budget
        fields = [
            "amount",
            "start_date",
            "end_date",
            "accounts",
            "categories",
            "all_accounts",
            "all_categories",
        ]
        widgets = {
            "start_date": CalendarWidget,
            "end_date": CalendarWidget,
            "all_accounts": ToggleWidget,
            "all_categories": ToggleWidget,
        }


class BudgetConfigurationForm(forms.ModelForm):
    """
    Budget configuration form
    """

    error_css_class = "error"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        shared_accounts = Account.objects.filter(
            group__members=self.request.user
        )
        owned_accounts = Account.objects.filter(
            owned_by=self.request.user, group=None
        )
        self.fields["accounts"].queryset = (
            shared_accounts | owned_accounts
        ).distinct()
        self.fields["accounts"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["frequency"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["start_date"].widget.type = "date"
        self.fields["start_date"].widget.format = "n/d/Y"
        created_categories = Category.objects.filter(
            created_by=self.request.user,
            internal_type=Category.DEFAULT,
            group=None,
            type=Category.EXPENSE,
        )
        shared_categories = Category.objects.filter(
            group__members=self.request.user, type=Category.EXPENSE
        )
        self.fields["categories"].queryset = (
            shared_categories | created_categories
        ).distinct()
        self.fields["categories"].widget.attrs.update({"class": "ui dropdown"})

    def save(self, *args, **kwargs):
        budget = self.instance
        if budget.pk is None:
            budget.created_by = self.request.user
        return super().save(*args, **kwargs)

    class Meta:
        model = BudgetConfiguration
        fields = [
            "amount",
            "start_date",
            "frequency",
            "accounts",
            "categories",
            "all_accounts",
            "all_categories",
            "active",
        ]
        widgets = {
            "active": ToggleWidget,
            "start_date": CalendarWidget,
            "all_accounts": ToggleWidget,
            "all_categories": ToggleWidget,
        }


class FakerForm(forms.Form):
    """
    Create instances of models
    """

    class ContentTypeModelChoiceField(forms.ModelChoiceField):
        """Custom ModelChoiceField that displays the model name as options"""

        def label_from_instance(self, obj):
            return obj.model

    model = ContentTypeModelChoiceField(
        queryset=ContentType.objects.filter(app_label="finance")
    )
    batch_amount = forms.IntegerField(max_value=100)
    target_user = forms.ModelChoiceField(User.objects.all())
    range_start = forms.DateField(required=False, widget=CalendarWidget)
    range_end = forms.DateField(required=False, widget=CalendarWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["model"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["target_user"].widget.attrs.update({"class": "ui dropdown"})
        self.fields["range_start"].widget.type = "date"
        self.fields["range_start"].widget.format = "n/d/Y"
        self.fields["range_start"].widget.attrs.update(
            {"placeholder": "Range Start"}
        )
        self.fields["range_end"].widget.type = "date"
        self.fields["range_end"].widget.format = "n/d/Y"
        self.fields["range_end"].widget.attrs.update(
            {"placeholder": "Range End"}
        )

    def create_fake_instances(self):
        """
        Create instances of a model
        """
        fake = Faker()
        fake.add_provider(lorem)

        batch_amount = self.cleaned_data["batch_amount"]
        model = self.cleaned_data["model"].model
        target_user = self.cleaned_data["target_user"]

        if self.cleaned_data["range_start"] is not None:
            range_start = timezone.make_aware(
                datetime.combine(
                    self.cleaned_data["range_start"], datetime.min.time()
                ),
                pytz.timezone("UTC"),
            )
        else:
            range_start = None

        if self.cleaned_data["range_end"] is not None:
            range_end = timezone.make_aware(
                datetime.combine(
                    self.cleaned_data["range_end"], datetime.min.time()
                ),
                pytz.timezone("UTC"),
            )
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
            return start + timedelta(seconds=random_second)

        if model == "transaction":
            for i in range(batch_amount):
                logger.info("Creating fake transaction #%s", i)

                if range_start is not None and range_end is not None:
                    timestamp = random_date(range_start, range_end)
                else:
                    timestamp = timezone.now()
                Transaction.objects.create(
                    description=fake.text(max_nb_chars=50, ext_word_list=None),
                    created_by=target_user,
                    timestamp=timestamp,
                    amount=randint(0, 1000),
                    category=Category.objects.filter(
                        created_by=target_user,
                        group=None,
                        internal_type=Category.DEFAULT,
                    )
                    .order_by("?")
                    .first(),
                    account=Account.objects.filter(
                        owned_by=target_user, group=None
                    )
                    .order_by("?")
                    .first(),
                )

            success, message = True, {
                "level": messages.SUCCESS,
                "message": f"Successfully created {batch_amount} fake instances of model {model}",
            }
            return success, message

        success, message = True, {
            "level": messages.ERROR,
            "message": f"No fake generator implemented for model {model}",
        }
        return success, message
