"""Finance's views"""
from datetime import datetime

import jwt
from __mono.mixins import PassRequestToFormViewMixin
from __mono.permissions import IsCreator
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, FloatField, Q, Sum, Value as V
from django.db.models.functions import Coalesce, TruncDay
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.dates import MonthArchiveView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView, DeleteView, FormView, UpdateView,
)
from django.views.generic.list import ListView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import (
    AccountForm, BudgetConfigurationForm, BudgetForm, CategoryForm, FakerForm,
    GoalForm, GroupForm, IconForm, InstallmentForm, RecurrentTransactionForm,
    TransactionForm, UniversalTransactionForm,
)
from .models import (
    Account, Budget, BudgetConfiguration, Category, Chart, Configuration, Goal,
    Group, Icon, Installment, Invite, RecurrentTransaction, Transaction,
    Transference, User,
)
from .serializers import ChartMoveSerializer, ChartSerializer


class HomePageView(LoginRequiredMixin, TemplateView):
    """Root view"""
    template_name = "finance/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            return context

        balance = 0
        for account in self.request.user.owned_accountset.all():
            balance += account.current_balance
        context["total_balance"] = balance

        transactions_this_month = Transaction.objects.filter(
            created_by=self.request.user,
            timestamp__range=[
                timezone.now() + relativedelta(months=-1),
                timezone.now()
            ],
        )
        transactions_last_month = Transaction.objects.filter(
            created_by=self.request.user,
            timestamp__range=[
                timezone.now() + relativedelta(months=-2),
                timezone.now() + relativedelta(months=-1)
            ]
        )

        expenses_this_month = transactions_this_month.filter(
            category__type=Category.EXPENSE
        ).aggregate(sum=Coalesce(Sum("amount"), V(0), output_field=FloatField()))
        incomes_this_month = transactions_this_month.filter(
            category__type=Category.INCOME
        ).aggregate(sum=Coalesce(Sum("amount"), V(0), output_field=FloatField()))
        expenses_last_month = transactions_last_month.filter(
            category__type=Category.EXPENSE
        ).aggregate(sum=Coalesce(Sum("amount"), V(0), output_field=FloatField()))
        incomes_last_month = transactions_last_month.filter(
            category__type=Category.INCOME
        ).aggregate(sum=Coalesce(Sum("amount"), V(0), output_field=FloatField()))
        context["expenses_this_month"] = round(expenses_this_month['sum'], 2)
        context["incomes_this_month"] = round(incomes_this_month['sum'], 2)
        context["expenses_last_month"] = round(expenses_last_month['sum'], 2)
        context["incomes_last_month"] = round(incomes_last_month['sum'], 2)

        closed_budgets = Budget.objects.filter(
            created_by=self.request.user,
            end_date__lt=datetime.combine(
                timezone.now().date(),
                datetime.min.time()
            )
        )
        open_budgets = Budget.objects.filter(
            created_by=self.request.user,
            start_date__lt=timezone.now(),
            end_date__gte=timezone.now(),
        )
        context["closed_budgets"] = closed_budgets
        context["open_budgets"] = open_budgets

        context["wallet"] = {
            a.name: a.current_balance
            for a in self.request.user.owned_accountset.all()
            if a.current_balance > 0
        }

        return context


class CardOrderView(LoginRequiredMixin, TemplateView):
    """Apply card movement"""
    template_name = "finance/card_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available_cards = Configuration.CARDS
        user_cards = self.request.user.configuration.cards_list

        # Generates a list of 3-tuples in the format (value, name, boolean)
        # value: code
        # name: human name
        # boolean: if user has selected
        cards = []
        if user_cards:
            for card in user_cards:
                cards.append(
                    (card, [name for value, name in available_cards if value == card][0], True)
                )
        for value, name in available_cards:
            if value not in [val for val, _, _ in cards]:
                cards.append(
                    (value, name, False)
                )

        context['cards'] = cards

        return context

    def post(self, request):
        """Apply card movement"""
        cards = request.POST.get('cards')
        configuration = request.user.configuration
        configuration.cards = cards
        configuration.save()
        return JsonResponse(
            {
                'success': True,
            }
        )


class TransactionListView(LoginRequiredMixin, ListView):
    """
    Display the list of :model:`finance.Transaction`.

    **Context**

    ``categories``
        List of :model:`finance.Category` to use in filter dropdown.
    ``daily_grouped``
        Queryset with trasaction data summarised by day.

    **Template:**

    :template:`finance/transaction_list.html`
    """
    model = Transaction
    paginate_by = 20
    template_name = 'finance/transaction_list.html'

    def get_queryset(self):
        qs = Transaction.objects.filter(
            created_by=self.request.user
        ).annotate(
            date=TruncDay('timestamp')
        ).order_by('-timestamp')

        category = self.request.GET.get('category', None)
        if category not in [None, ""]:
            qs = qs.filter(category__in=category.split(','))

        account = self.request.GET.get('account', None)
        if account not in [None, ""]:
            qs = qs.filter(account__in=account.split(','))

        future = self.request.GET.get('future', None)
        if future in [None, ""]:
            qs = qs.filter(timestamp__date__lte=timezone.now().date())

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        context['categories'] = Category.objects.filter(
            created_by=self.request.user, internal_type=Category.DEFAULT)
        category = self.request.GET.get('category', None)
        if category not in [None, ""]:
            context['filtered_categories'] = category.split(',')

        context['accounts'] = Account.objects.filter(
            owned_by=self.request.user)
        account = self.request.GET.get('account', None)
        if account not in [None, ""]:
            context['filtered_accounts'] = account.split(',')

        qs = self.get_queryset()
        qs = qs.annotate(
            date=TruncDay('timestamp')
        ).values('date')
        qs = qs.annotate(
            total_expense=Coalesce(
                Sum(
                    'amount',
                    filter=Q(category__type='EXP')
                ), V(0), output_field=FloatField()
            ),
            total_income=Coalesce(
                Sum(
                    'amount',
                    filter=Q(category__type='INC')
                ), V(0), output_field=FloatField()
            )
        )
        qs = qs.order_by('-date')

        context['daily_grouped'] = qs

        query_string = self.request.GET.copy()
        if "page" in query_string:
            query_string.pop('page')

        context['query_string'] = query_string.urlencode()

        transaction_types = Category.TRANSACTION_TYPES.copy()
        transaction_types.append(("TRF", _("Transfer")))
        context['transaction_types'] = transaction_types

        context['frequency'] = RecurrentTransaction.FREQUENCY
        context['remainder'] = Installment.HANDLE_REMAINDER

        return context


class TransactionCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, FormView):
    """Create transaction"""
    template_name = "finance/universal_transaction_form.html"
    form_class = UniversalTransactionForm
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was created successfully"

    def form_valid(self, form):
        data = form.cleaned_data
        is_recurrent_or_installment = data.pop("is_recurrent_or_installment")
        recurrent_or_installment = data.pop("recurrent_or_installment")
        data["created_by"] = self.request.user

        if data['type'] == "TRF":
            # For Transference
            del data["frequency"]
            del data["months"]
            del data['handle_remainder']
            del data["account"]
            del data["category"]
            del data["type"]
            del data["active"]
            transference = Transference(**data)
            transference.save()
        else:
            del data["type"]
            del data['from_account']
            del data['to_account']
            if is_recurrent_or_installment:
                if recurrent_or_installment == "R":
                    # For Recurrent Transaction
                    del data['months']
                    del data['handle_remainder']
                    recurrent_transaction = RecurrentTransaction(**data)
                    recurrent_transaction.save()
                elif recurrent_or_installment == "I":
                    # For Installment
                    del data['frequency']
                    del data['active']
                    data["total_amount"] = data.pop("amount")
                    installment = Installment(**data)
                    installment.save()
            else:
                # For Transaction
                del data["frequency"]
                del data["months"]
                del data['handle_remainder']
                transaction = Transaction(**data)
                transaction.save()

        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """Update transaction"""
    model = Transaction
    form_class = TransactionForm
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was updated successfully"


class TransactionDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete transaction"""
    model = Transaction
    success_url = reverse_lazy('finance:transactions')
    success_message = _("Transaction was deleted successfully")

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class TransactionMonthArchiveView(LoginRequiredMixin, MonthArchiveView):  # pylint: disable=too-many-ancestors
    """List transactions monthly"""
    queryset = Transaction.objects.all()
    date_field = "timestamp"
    allow_future = True
    allow_empty = True

    def get_queryset(self):
        """Apply filters"""
        qs = Transaction.objects.filter(created_by=self.request.user)

        category = self.request.GET.get('category', '')
        if category != '':
            qs = qs.filter(category__in=category.split(','))

        account = self.request.GET.get('account', '')
        if account != '':
            qs = qs.filter(account__in=account.split(','))

        return qs

    def get_context_data(self, **kwargs):
        """Add eextra context"""
        context = super().get_context_data(**kwargs)
        context['weekday'] = context['month'].isoweekday()
        context['weekday_range'] = range(context['month'].isoweekday())
        context['month_range'] = range((context['next_month'] - context['month']).days)

        context['categories'] = Category.objects.filter(created_by=self.request.user, internal_type=Category.DEFAULT)
        category = self.request.GET.get('category', '')
        if category != '':
            context['filtered_categories'] = category.split(',')

        context['accounts'] = Account.objects.filter(owned_by=self.request.user)
        account = self.request.GET.get('account', '')
        if account != '':
            context['filtered_accounts'] = account.split(',')

        qs = context['object_list']
        qs = qs.annotate(
            date=TruncDay('timestamp')
        ).values('date')
        qs = qs.annotate(
            total_expense=Coalesce(
                Sum(
                    'amount',
                    filter=Q(category__type='EXP')
                ), V(0), output_field=FloatField()
            ),
            total_income=Coalesce(
                Sum(
                    'amount',
                    filter=Q(category__type='INC')
                ), V(0), output_field=FloatField()
            )
        )
        qs = qs.order_by('-date')
        context['daily_grouped'] = qs
        return context


class RecurrentTransactionListView(LoginRequiredMixin, ListView):
    """List recurrent transactions"""
    model = RecurrentTransaction

    def get_queryset(self):
        return RecurrentTransaction.objects.filter(
            created_by=self.request.user
        ).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['frequencies'] = RecurrentTransaction.FREQUENCY
        return context


class RecurrentTransactionCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """Create recurrent transaction"""
    model = RecurrentTransaction
    form_class = RecurrentTransactionForm
    success_url = reverse_lazy('finance:recurrent_transactions')
    success_message = "%(description)s was created successfully"


class RecurrentTransactionUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """Edit recurrent transaction"""
    model = RecurrentTransaction
    form_class = RecurrentTransactionForm
    success_url = reverse_lazy('finance:recurrent_transactions')
    success_message = "%(description)s was updated successfully"


class RecurrentTransactionDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete recurrent transaction"""
    model = RecurrentTransaction
    success_url = reverse_lazy('finance:recurrent_transactions')
    success_message = _("Transaction was deleted successfully")

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class InstallmentListView(LoginRequiredMixin, ListView):
    """List installments"""
    model = Installment

    def get_queryset(self):
        return Installment.objects.filter(
            created_by=self.request.user
        ).order_by('-timestamp')


class InstallmentCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """Create installment"""
    model = Installment
    form_class = InstallmentForm
    success_url = reverse_lazy('finance:installments')
    success_message = "%(description)s was created successfully"


class InstallmentUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """Edit installment"""
    model = Installment
    form_class = InstallmentForm
    success_url = reverse_lazy('finance:installments')
    success_message = "%(description)s was updated successfully"


class InstallmentDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete installment"""
    model = Installment
    success_url = reverse_lazy('finance:installments')
    success_message = _("Installment group was deleted successfully")

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class AccountListView(LoginRequiredMixin, ListView):
    """List accounts"""
    model = Account

    def get_context_data(self, **kwargs):
        """Add extra context"""
        context = super().get_context_data(**kwargs)
        groups = self.request.user.shared_groupset.all()
        context['groups'] = groups
        members = [m.id for g in groups for m in g.members.all()]
        context['members'] = User.objects.filter(id__in=members).exclude(id=self.request.user.id)
        return context

    def get_queryset(self):
        """Apply filters"""
        owned_accounts = self.request.user.owned_accountset.all()
        shared_accounts = Account.objects.filter(group__members=self.request.user)
        qs = (owned_accounts | shared_accounts).distinct()

        group = self.request.GET.get('group', '')
        if group != '':
            qs = qs.filter(group=group)

        member = self.request.GET.get('member', '')
        if member != '':
            qs = qs.filter(group__members=member)

        return qs


class AccountDetailView(LoginRequiredMixin, DetailView):
    """Retrieve account"""
    model = Account


class AccountCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """Create account"""
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('finance:accounts')
    success_message = "%(name)s was created successfully"


class AccountUpdateView(UserPassesTestMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """Edit account"""
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('finance:accounts')
    success_message = "%(name)s was updated successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user


class AccountDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete account"""
    model = Account
    success_url = reverse_lazy('finance:accounts')
    success_message = "Account was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class GroupListView(LoginRequiredMixin, ListView):
    """List groups"""
    model = Group

    def get_context_data(self, **kwargs):
        """Add extra context"""
        context = super().get_context_data(**kwargs)
        groups = Group.objects.filter(members=self.request.user)
        members = [m.id for g in groups for m in g.members.all()]
        context['members'] = User.objects.filter(id__in=members).exclude(id=self.request.user.id)
        return context

    def get_queryset(self):
        """Apply filters"""
        qs = Group.objects.filter(members=self.request.user)

        member = self.request.GET.get('member', '')
        if member != '':
            qs = qs.filter(members=member)

        return qs


class GroupCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """Create group"""
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('finance:groups')
    success_message = "%(name)s was created successfully"


class GroupUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """Update group"""
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('finance:groups')
    success_message = "%(name)s was updated successfully"


class GroupDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete group"""
    model = Group
    success_url = reverse_lazy('finance:groups')
    success_message = "Group was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class CategoryListView(LoginRequiredMixin, ListView):
    """List categories"""
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = Category.TRANSACTION_TYPES
        return context

    def get_queryset(self):
        """Apply filters"""
        qs = Category.objects.filter(
            created_by=self.request.user,
            internal_type=Category.DEFAULT
        )

        category_type = self.request.GET.get('type', '')
        if category_type != '':
            qs = qs.filter(type=category_type)

        return qs


class CategoryListApi(View):
    """List categories"""

    def get(self, request):
        """List categories"""
        category_type = request.GET.get("type", '')
        account = request.GET.get("account", '')
        if category_type != '':
            qs = Category.objects.filter(
                created_by=request.user,
                type=category_type,
                internal_type=Category.DEFAULT
            )
        else:
            qs = Category.objects.none()
            return JsonResponse(
                {
                    'success': True,
                    'message': 'Categories retrived from database.',
                    'results': list(qs),
                }
            )

        if account != '':
            account = Account.objects.get(id=int(account))
            qs = qs.filter(group=account.group)
        else:
            qs = qs.filter(group=None)

        qs = qs.values('name').annotate(
            value=F('id'),
            icon=F('icon__markup'),
        )
        return JsonResponse(
            {
                'success': True,
                'message': 'Categories retrived from database.',
                'results': list(qs),
            }
        )


class CategoryCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """Create category"""
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('finance:categories')
    success_message = "%(name)s was created successfully"


class CategoryUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """Update category"""
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('finance:categories')
    success_message = "%(name)s was updated successfully"


class CategoryDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete category"""
    model = Category
    success_url = reverse_lazy('finance:categories')
    success_message = "Category was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class IconListView(UserPassesTestMixin, ListView):
    """List icons"""
    model = Icon

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        qs = Icon.objects.all()
        return qs


class IconCreateView(UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """Create icon"""
    model = Icon
    form_class = IconForm
    success_url = reverse_lazy('finance:icons')
    success_message = "%(markup)s was created successfully"

    def test_func(self):
        return self.request.user.is_superuser


class IconUpdateView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """Update icon"""
    model = Icon
    form_class = IconForm
    success_url = reverse_lazy('finance:icons')
    success_message = "%(markup)s was updated successfully"

    def test_func(self):
        return self.request.user.is_superuser


class IconDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete icon"""
    model = Icon
    success_url = reverse_lazy('finance:icons')
    success_message = "Icon was deleted successfully"

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class GoalListView(LoginRequiredMixin, ListView):
    """List goals"""
    model = Goal

    def get_queryset(self):
        qs = Goal.objects.all()
        return qs


class GoalCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """Create goal"""
    model = Goal
    form_class = GoalForm
    success_url = reverse_lazy('finance:goals')
    success_message = "%(name)s was created successfully"


class GoalUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """Update goal"""
    model = Goal
    form_class = GoalForm
    success_url = reverse_lazy('finance:goals')
    success_message = "%(name)s was updated successfully"


class GoalDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Delete goal"""
    model = Goal
    success_url = reverse_lazy('finance:goals')
    success_message = "Goal was deleted successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class InviteApi(LoginRequiredMixin, View):
    """Create invite"""

    def post(self, request):
        """Create invite"""
        group_id = request.POST.get("group")
        email = request.POST.get("email")
        user = request.user
        group = Group.objects.get(id=int(group_id))

        if Invite.objects.filter(email=email, group=group).exists():
            response = {
                'success': True,
                'message': f"You've already invited {email} to this group."
            }
        elif email == '':
            response = {
                'success': False,
                'message': 'Email cannot be empty.'
            }
        else:
            invite = Invite(
                group=group,
                email=email,
                created_by=user
            )
            invite.save()
            invite.send(request)
            response = {
                'success': True,
                'message': 'Invite created.',
                'results': invite.pk,
            }
        return JsonResponse(response)


class InviteListApiView(View):
    """List invites"""

    def get(self, request, *args, **kwargs):
        """List invites"""
        group_id = request.GET.get("group")
        group = Group.objects.get(id=int(group_id))

        qs = Invite.objects.filter(group=group, accepted=False).values('email')

        if qs.count() == 0:
            response = {
                'success': True,
                'message': "No invites found.",
                'results': None
            }
        else:
            response = {
                'success': True,
                'message': "List of invites.",
                'results': list(qs)
            }
        return JsonResponse(response)


class InviteAcceptanceView(LoginRequiredMixin, TemplateView):
    """Accept invitation"""
    template_name = "finance/invite_acceptance.html"

    def get(self, request, *args, **kwargs):
        """Accept invitation"""
        token = request.GET.get('t', None)

        if token is None:
            return HttpResponse("error")

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        invite = get_object_or_404(Invite, pk=payload['id'])
        user_already_member = request.user in invite.group.members.all()
        if not invite.accepted and not user_already_member:
            invite.accept(request.user)
            invite.save()
        return self.render_to_response({
            "accepted": invite.accepted,
            "user_already_member": user_already_member,
        })


class BudgetListView(LoginRequiredMixin, ListView):
    """
    List budgets
    """
    model = Budget

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(created_by=self.request.user, internal_type=Category.DEFAULT)
        context['accounts'] = Account.objects.filter(owned_by=self.request.user)
        return context

    def get_queryset(self):
        """Apply filters"""
        qs = Budget.objects.filter(
            created_by=self.request.user,
            start_date__lte=timezone.now().date()
        )

        category = self.request.GET.get('category', '')
        if category != '':
            qs = qs.filter(categories=category)

        account = self.request.GET.get('account', '')
        if account != '':
            qs = qs.filter(accounts=account)

        return qs


class BudgetCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """
    Create budget
    """
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('finance:budgets')
    success_message = "Budget was created successfully"


class BudgetUpdateView(UserPassesTestMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """
    Update budget
    """
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('finance:budgets')
    success_message = "Budget was updated successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user


class BudgetDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    Delete budget
    """
    model = Budget
    success_url = reverse_lazy('finance:budgets')
    success_message = "Budget was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class BudgetConfigurationListView(LoginRequiredMixin, ListView):
    """
    List BudgetConfiguration
    """
    model = BudgetConfiguration

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(created_by=self.request.user, internal_type=Category.DEFAULT)
        context['accounts'] = Account.objects.filter(owned_by=self.request.user)
        return context

    def get_queryset(self):
        """Apply filters"""
        qs = BudgetConfiguration.objects.filter(created_by=self.request.user)

        category = self.request.GET.get('category', '')
        if category != '':
            qs = qs.filter(categories=category)

        account = self.request.GET.get('account', '')
        if account != '':
            qs = qs.filter(accounts=account)

        return qs


class BudgetConfigurationCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    """
    Create BudgetConfiguration
    """
    model = BudgetConfiguration
    form_class = BudgetConfigurationForm
    success_url = reverse_lazy('finance:budgetconfigurations')
    success_message = "BudgetConfiguration was created successfully"


class BudgetConfigurationUpdateView(UserPassesTestMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    """
    Update BudgetConfiguration
    """
    model = BudgetConfiguration
    form_class = BudgetConfigurationForm
    success_url = reverse_lazy('finance:budgetconfigurations')
    success_message = "BudgetConfiguration was updated successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user


class BudgetConfigurationDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    Delete BudgetConfiguration
    """
    model = BudgetConfiguration
    success_url = reverse_lazy('finance:budgetconfigurations')
    success_message = "BudgetConfiguration was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class FakerView(UserPassesTestMixin, FormView):
    """
    Create fake instances
    """
    template_name = "finance/faker.html"
    form_class = FakerForm
    success_url = "/fn/faker/"

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form) -> HttpResponse:
        """
        Create fake instances
        """
        _, message = form.create_fake_instances()
        messages.add_message(
            self.request,
            message['level'],
            message['message']
        )
        return super().form_valid(form)


class RestrictedAreaView(LoginRequiredMixin, TemplateView):
    """
    Restricted area
    """
    template_name = "finance/restricted_area.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(
            is_active=True).exclude(
                id=self.request.user.id)
        return context


class ChartsView(LoginRequiredMixin, TemplateView):
    """View all charts"""
    template_name = "finance/charts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chart_types'] = Chart.TYPE_CHOICES
        context['chart_metrics'] = Chart.METRIC_CHOICES
        context['chart_fields'] = Chart.FIELD_CHOICES
        context['chart_axes'] = Chart.AXIS_CHOICES
        context['chart_categories'] = Chart.CATEGORY_CHOICES
        context['chart_filters'] = Chart.FILTER_CHOICES
        return context


class ChartDataApiView(LoginRequiredMixin, APIView):
    """
    Retrieve, update or delete chart
    """

    permission_classes = [IsCreator]

    def get(self, request, pk):
        """Retrieve chart data"""
        chart = get_object_or_404(Chart, pk=pk)
        data = chart.get_queryset(request.user)
        return Response({
            'success': True,
            'data': {
                'data_points': data,
                'field_display': chart.get_field_display(),
                'title': chart.title,
                'type': chart.type,
                'metric': chart.metric,
                'field': chart.field,
                'axis': chart.axis,
                'category': chart.category,
                'filters': chart.filters,
            },
        })

    def put(self, request, pk):
        """Edit chart"""
        chart = get_object_or_404(Chart, pk=pk)
        serializer = ChartSerializer(chart, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'success': True,
            'data': serializer.data,
        })

    def patch(self, request, pk):
        """Edit chart"""
        chart = get_object_or_404(Chart, pk=pk)
        serializer = ChartSerializer(chart, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'success': True,
            'data': serializer.data,
        })

    def delete(self, request, pk):
        """Delete a chart"""
        chart = get_object_or_404(Chart, pk=pk)
        chart.delete()
        return Response({
            'success': True,
        })


class ChartListApiView(LoginRequiredMixin, APIView):
    """
    List or create charts
    """

    def get(self, request):
        """List all user's charts"""
        charts = request.user.charts.all()
        return Response({
            'success': True,
            'data': [c.id for c in charts]
        })

    def post(self, request):
        """Create new chart"""
        serializer = ChartSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'success': True,
            'data': serializer.data,
        })


class ChartMoveApiView(LoginRequiredMixin, APIView):
    """
    Apply chart movement
    """
    def post(self, request):
        """
        Apply chart movement
        """
        serializer = ChartMoveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.move()
            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
