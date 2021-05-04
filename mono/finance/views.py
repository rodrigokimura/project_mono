from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404, redirect
from django.urls.base import reverse
from django.views import View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.dates import MonthArchiveView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetDoneView, PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Q, Sum, Value as V, FloatField
from django.db.models.functions import Coalesce, TruncDay
from django.utils.translation import gettext as _
from django.utils import timezone
from rest_framework import authentication, permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from .models import (BudgetConfiguration, Configuration, Installment, Transaction, Account, Group,
                     Category, Icon, Goal, Invite, Notification, Budget, Plan,
                     Subscription, RecurrentTransaction, Transference)
from .forms import (
    BudgetConfigurationForm, InstallmentForm, TransactionForm, GroupForm,
    CategoryForm, UserForm, AccountForm, IconForm, GoalForm, FakerForm,
    BudgetForm, RecurrentTransactionForm, UniversalTransactionForm)
from .serializers import UserSerializer, TransactionSerializer
import time
import jwt
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import pytz
from datetime import datetime
from social_django.models import UserSocialAuth


class TokenMixin(object):
    def get_context_data(self, **kwargs):
        context = super(TokenMixin, self).get_context_data(**kwargs)
        token = self.kwargs['token']

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        context['id'] = payload['id']
        return context


class PassRequestToFormViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class HomePageView(TemplateView):
    template_name = "finance/index.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect(reverse("finance:login"))

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            return context

        balance = 0
        for a in self.request.user.owned_accountset.all():
            balance += a.current_balance
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

        return context


class CardOrderView(TemplateView):
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
                    (card, [n for v, n in available_cards if v == card][0], True)
                )
        for v, n in available_cards:
            if v not in [v for v, n, b in cards]:
                cards.append(
                    (v, n, False)
                )

        context['cards'] = cards

        return context

    def post(self, request):
        cards = request.POST.get('cards')
        configuration = request.user.configuration
        configuration.cards = cards
        configuration.save()
        return JsonResponse(
            {
                'success': True,
            }
        )


class SignUp(SuccessMessageMixin, PassRequestToFormViewMixin, CreateView):
    form_class = UserForm
    template_name = "finance/signup.html"
    success_url = reverse_lazy('finance:index')
    success_message = "%(username)s user created successfully"

    def save(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        login(self.request, self.get_user())
        return super(SignUp, self).save(request, *args, **kwargs)


class Login(LoginView):
    template_name = "finance/login.html"


class Logout(LogoutView):
    next_page = reverse_lazy('finance:index')


class PasswordResetView(PasswordResetView):
    success_url = reverse_lazy('finance:password_reset_done')
    title = _('Password reset')
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    template_name = 'registration/password_reset_form.html'
    extra_email_context = {
        "expiration_time_hours": int(settings.PASSWORD_RESET_TIMEOUT / 60 / 60)
    }


class PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('finance:password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'
    title = _('Enter new password')


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'
    title = _('Password reset sent')


class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
    title = _('Password reset complete')


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

        return context


class TransactionCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, FormView):
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
    model = Transaction
    form_class = TransactionForm
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was updated successfully"


class TransactionDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy('finance:transactions')
    success_message = _("Transaction was deleted successfully")

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(TransactionDeleteView, self).delete(request, *args, **kwargs)


class TransactionMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
    queryset = Transaction.objects.all()
    date_field = "timestamp"
    allow_future = True
    allow_empty = True

    def get_queryset(self):
        qs = Transaction.objects.filter(created_by=self.request.user)

        category = self.request.GET.get('category', None)
        if category not in [None, ""]:
            qs = qs.filter(category__in=category.split(','))

        account = self.request.GET.get('account', None)
        if account not in [None, ""]:
            qs = qs.filter(account__in=account.split(','))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weekday'] = context['month'].isoweekday()
        context['weekday_range'] = range(context['month'].isoweekday())
        context['month_range'] = range((context['next_month'] - context['month']).days)

        context['categories'] = Category.objects.filter(created_by=self.request.user, internal_type=Category.DEFAULT)
        category = self.request.GET.get('category', None)
        if category not in [None, ""]:
            context['filtered_categories'] = category.split(',')

        context['accounts'] = Account.objects.filter(owned_by=self.request.user)
        account = self.request.GET.get('account', None)
        if account not in [None, ""]:
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
    model = RecurrentTransaction

    def get_queryset(self):
        qs = RecurrentTransaction.objects.filter(
            created_by=self.request.user
        ).order_by('-timestamp')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['frequencies'] = RecurrentTransaction.FREQUENCY
        return context


class RecurrentTransactionCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = RecurrentTransaction
    form_class = RecurrentTransactionForm
    success_url = reverse_lazy('finance:recurrent_transactions')
    success_message = "%(description)s was created successfully"


class RecurrentTransactionUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = RecurrentTransaction
    form_class = RecurrentTransactionForm
    success_url = reverse_lazy('finance:recurrent_transactions')
    success_message = "%(description)s was updated successfully"


class RecurrentTransactionDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = RecurrentTransaction
    success_url = reverse_lazy('finance:recurrent_transactions')
    success_message = _("Transaction was deleted successfully")

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(RecurrentTransactionDeleteView, self).delete(request, *args, **kwargs)


class InstallmentListView(LoginRequiredMixin, ListView):
    model = Installment

    def get_queryset(self):
        qs = Installment.objects.filter(
            created_by=self.request.user
        ).order_by('-timestamp')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class InstallmentCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Installment
    form_class = InstallmentForm
    success_url = reverse_lazy('finance:installments')
    success_message = "%(description)s was created successfully"


class InstallmentUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Installment
    form_class = InstallmentForm
    success_url = reverse_lazy('finance:installments')
    success_message = "%(description)s was updated successfully"


class InstallmentDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Installment
    success_url = reverse_lazy('finance:installments')
    success_message = _("Installment group was deleted successfully")

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(InstallmentDeleteView, self).delete(request, *args, **kwargs)


class AccountListView(LoginRequiredMixin, ListView):
    model = Account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = self.request.user.shared_groupset.all()
        context['groups'] = groups
        members = [m.id for g in groups for m in g.members.all()]
        context['members'] = User.objects.filter(id__in=members).exclude(id=self.request.user.id)
        return context

    def get_queryset(self):
        owned_accounts = self.request.user.owned_accountset.all()
        shared_accounts = Account.objects.filter(group__members=self.request.user)
        qs = (owned_accounts | shared_accounts).distinct()

        group = self.request.GET.get('group', None)
        if group not in [None, ""]:
            qs = qs.filter(group=group)

        member = self.request.GET.get('member', None)
        if member not in [None, ""]:
            qs = qs.filter(group__members=member)

        return qs


class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account


class AccountCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('finance:accounts')
    success_message = "%(name)s was created successfully"


class AccountUpdateView(UserPassesTestMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('finance:accounts')
    success_message = "%(name)s was updated successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user


class AccountDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Account
    success_url = reverse_lazy('finance:accounts')
    success_message = "Account was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(AccountDeleteView, self).delete(request, *args, **kwargs)


class GroupListView(LoginRequiredMixin, ListView):
    model = Group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = Group.objects.filter(members=self.request.user)
        members = [m.id for g in groups for m in g.members.all()]
        context['members'] = User.objects.filter(id__in=members).exclude(id=self.request.user.id)
        return context

    def get_queryset(self):
        qs = Group.objects.filter(members=self.request.user)

        member = self.request.GET.get('member', None)
        if member not in [None, ""]:
            qs = qs.filter(members=member)

        return qs


class GroupCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('finance:groups')
    success_message = "%(name)s was created successfully"


class GroupUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('finance:groups')
    success_message = "%(name)s was updated successfully"


class GroupDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('finance:groups')
    success_message = "Group was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(GroupDeleteView, self).delete(request, *args, **kwargs)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = Category.TRANSACTION_TYPES
        return context

    def get_queryset(self):
        qs = Category.objects.filter(
            created_by=self.request.user,
            internal_type=Category.DEFAULT
        )

        type = self.request.GET.get('type', None)
        if type not in [None, ""]:
            qs = qs.filter(type=type)

        return qs


class CategoryListApi(View):
    def get(self, request):
        time.sleep(.5)
        type = request.GET.get("type")
        account = request.GET.get("account")
        if type not in [None, ""]:
            qs = Category.objects.filter(
                created_by=request.user,
                type=type,
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

        if account not in [None, ""]:
            account = Account.objects.get(id=int(account))
            qs = qs.filter(group=account.group)
        else:
            qs = qs.filter(group=None)

        qs = qs.values('name')
        qs = qs.annotate(
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
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('finance:categories')
    success_message = "%(name)s was created successfully"


class CategoryUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('finance:categories')
    success_message = "%(name)s was updated successfully"


class CategoryDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('finance:categories')
    success_message = "Category was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        if self.get_object().is_deletable:
            messages.success(self.request, self.success_message)
            return super(CategoryDeleteView, self).delete(request, *args, **kwargs)
        else:
            messages.warning(self.request, "Standard categories cannot be deleted.")
            return redirect('finance:categories')


class IconListView(UserPassesTestMixin, ListView):
    model = Icon

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        qs = Icon.objects.all()
        return qs


class IconCreateView(UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Icon
    form_class = IconForm
    success_url = reverse_lazy('finance:icons')
    success_message = "%(markup)s was created successfully"

    def test_func(self):
        return self.request.user.is_superuser


class IconUpdateView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Icon
    form_class = IconForm
    success_url = reverse_lazy('finance:icons')
    success_message = "%(markup)s was updated successfully"

    def test_func(self):
        return self.request.user.is_superuser


class IconDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Icon
    success_url = reverse_lazy('finance:icons')
    success_message = "Icon was deleted successfully"

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(IconDeleteView, self).delete(request, *args, **kwargs)


class GoalListView(LoginRequiredMixin, ListView):
    model = Goal

    def get_queryset(self):
        qs = Goal.objects.all()
        return qs


class GoalCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Goal
    form_class = GoalForm
    success_url = reverse_lazy('finance:goals')
    success_message = "%(name)s was created successfully"


class GoalUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Goal
    form_class = GoalForm
    success_url = reverse_lazy('finance:goals')
    success_message = "%(name)s was updated successfully"


class GoalDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Goal
    success_url = reverse_lazy('finance:goals')
    success_message = "Goal was deleted successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(GoalDeleteView, self).delete(request, *args, **kwargs)


class InviteApi(LoginRequiredMixin, View):

    def post(self, request):
        time.sleep(2)
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
    def get(self, request):
        time.sleep(1)
        group_id = request.GET.get("group")
        user = request.user
        group = Group.objects.get(id=int(group_id))

        if user in group.members.all():
            pass
        else:
            print("not in")

        qs = Invite.objects.filter(group=group, accepted=False)
        qs = qs.values('email')

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
    template_name = "finance/invite_acceptance.html"

    def get(self, request):
        token = request.GET.get('t', None)

        if token is None:
            return HttpResponse("error")
        else:
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


class NotificationListApi(LoginRequiredMixin, View):
    def get(self, request):
        time.sleep(.5)
        qs = Notification.objects.filter(
            to=request.user,
            active=True,
            read_at=None
        ).values('id').annotate(
            value=F('id'),
            name=F('title'),
            description=F('message'),
            icon=F('icon__markup'))
        return JsonResponse(
            {
                'success': True,
                'message': 'Notifications retrived from database.',
                'results': list(qs)
            }
        )


class NotificationAction(LoginRequiredMixin, RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        notification = get_object_or_404(Notification, pk=kwargs['pk'])
        if notification.to == self.request.user:
            notification.mark_as_read()
            if notification.action:
                self.url = notification.action
            else:
                self.url = reverse("finance:index")
        return super().get_redirect_url(*args, **kwargs)


class NotificationCheckUnread(LoginRequiredMixin, View):
    def get(self, request):
        results = Notification.objects.filter(
            to=request.user,
            active=True,
            read_at=None
        ).values('id')
        return JsonResponse(
            {
                'success': True,
                'results': [r['id'] for r in results],
            }
        )


class NotificationMarkAsRead(LoginRequiredMixin, View):
    def post(self, request):
        id = request.POST.get('id')
        qs = Notification.objects.filter(to=request.user)
        if id == '*' and qs.exists():
            for notification in qs:
                notification.mark_as_read()
            return JsonResponse({'success': True})
        else:
            notification = get_object_or_404(Notification, id=request.POST.get('id'))
            if notification.to == request.user:
                notification.mark_as_read()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(created_by=self.request.user, internal_type=Category.DEFAULT)
        context['accounts'] = Account.objects.filter(owned_by=self.request.user)
        return context

    def get_queryset(self):
        qs = Budget.objects.filter(
            created_by=self.request.user,
            start_date__lte=timezone.now().date()
        )

        category = self.request.GET.get('category', None)
        if category not in [None, ""]:
            qs = qs.filter(categories=category)

        account = self.request.GET.get('account', None)
        if account not in [None, ""]:
            qs = qs.filter(accounts=account)

        return qs


class BudgetCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('finance:budgets')
    success_message = "Budget was created successfully"


class BudgetUpdateView(UserPassesTestMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('finance:budgets')
    success_message = "Budget was updated successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user


class BudgetDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Budget
    success_url = reverse_lazy('finance:budgets')
    success_message = "Budget was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(BudgetDeleteView, self).delete(request, *args, **kwargs)


class BudgetConfigurationListView(LoginRequiredMixin, ListView):
    model = BudgetConfiguration

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['categories'] = Category.objects.filter(created_by=self.request.user, internal_type=Category.DEFAULT)
        context['accounts'] = Account.objects.filter(owned_by=self.request.user)
        return context

    def get_queryset(self):
        qs = BudgetConfiguration.objects.filter(created_by=self.request.user)

        category = self.request.GET.get('category', None)
        if category not in [None, ""]:
            qs = qs.filter(categories=category)

        account = self.request.GET.get('account', None)
        if account not in [None, ""]:
            qs = qs.filter(accounts=account)

        return qs


class BudgetConfigurationCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = BudgetConfiguration
    form_class = BudgetConfigurationForm
    success_url = reverse_lazy('finance:budgetconfigurations')
    success_message = "BudgetConfiguration was created successfully"


class BudgetConfigurationUpdateView(UserPassesTestMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = BudgetConfiguration
    form_class = BudgetConfigurationForm
    success_url = reverse_lazy('finance:budgetconfigurations')
    success_message = "BudgetConfiguration was updated successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user


class BudgetConfigurationDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = BudgetConfiguration
    success_url = reverse_lazy('finance:budgetconfigurations')
    success_message = "BudgetConfiguration was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(BudgetConfigurationDeleteView, self).delete(request, *args, **kwargs)


class FakerView(UserPassesTestMixin, FormView):
    template_name = "finance/faker.html"
    form_class = FakerForm
    success_url = "/fn/faker/"

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form) -> HttpResponse:

        success, message = form.create_fake_instances()
        messages.add_message(self.request, message['level'], message['message'])

        return super().form_valid(form)


class PlansView(UserPassesTestMixin, TemplateView):
    template_name = "finance/plans.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Get all Stripe products
        products = stripe.Product.list(limit=100, active=True).data
        if len(products) == 100:
            next_page = True
            max_loops = 10
            loop = 0
            last_product = products[-1]
            while next_page and loop < max_loops:
                loop += 1
                new_products = stripe.Product.list(limit=100, starting_after=last_product).data
                if len(new_products) == 100:
                    products.extend(new_products)
                    last_product = new_products[-1]
                else:
                    next_page = False

        # Filter products by metada {app:finance}
        products = filter(lambda product: hasattr(product.metadata, 'app'), products)
        products = [product for product in products if product.metadata.app == 'finance']

        # Sort products according to business rules
        pass

        context['plans'] = Plan.objects.filter(product_id__in=[product.id for product in products])
        context['free_plan'] = Plan.objects.filter(
            product_id__in=[product.id for product in products],
            type=Plan.FREE
        ).first()
        if self.request.user.is_authenticated:
            if Subscription.objects.filter(user=self.request.user).exists():
                user_plan = Subscription.objects.get(user=self.request.user).plan
            else:
                user_plan = Plan.objects.get(type=Plan.FREE)
        else:
            user_plan = None
        context['user_plan'] = user_plan

        return context


class CheckoutView(UserPassesTestMixin, TemplateView):
    template_name = "finance/checkout.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_pk'] = settings.STRIPE_PUBLIC_KEY
        # Check query param 'plan'
        plan_id = self.request.GET.get("plan", None)
        if plan_id not in ["", None]:
            plan = get_object_or_404(Plan, pk=plan_id)
            context['plan'] = plan
        else:
            raise SuspiciousOperation("Invalid request. This route need a query parameter 'plan'.")

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            product = stripe.Product.retrieve(plan.product_id)
            context['product'] = product
        except Exception as e:
            print(e)
            raise SuspiciousOperation(e)

        # Get currency from language
        if self.request.LANGUAGE_CODE == 'pt-br':
            currency = 'brl'
        else:
            currency = 'usd'

        # Get Plans for the plan
        plans = stripe.Plan.list(product=product.id, active=True, currency=currency).data

        # Get monthly plan price
        plans_for_context = []
        try:
            monthly_price = list(filter(lambda price: price.interval == 'month', plans))[0]
            plans_for_context.append(monthly_price)
        except Exception as e:
            print(e)

        # Get yearly plan price
        try:
            yearly_price = list(filter(lambda price: price.interval == 'year', plans))[0]
            plans_for_context.append(yearly_price)
        except Exception as e:
            print(e)

        context['plans'] = plans_for_context

        return context

    def get(self, request):
        plan_id = self.request.GET.get("plan", None)
        plan = get_object_or_404(Plan, pk=plan_id)
        if plan.type == Plan.FREE:
            if Subscription.objects.filter(user=request.user).exists():
                subscription = Subscription.objects.get(user=request.user)

                (success, message) = subscription.cancel_at_period_end()
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)
                return redirect(to=reverse('finance:plans'))
            else:
                messages.error(request, "You are already subscribed to the Free Plan.")
                return redirect(to=reverse('finance:plans'))
        else:
            return self.render_to_response(self.get_context_data())

    def post(self, request):
        payment_method_id = request.POST.get("payment_method_id")
        price_id = request.POST.get("price_id")

        stripe.api_key = settings.STRIPE_SECRET_KEY

        email = self.request.user.email

        # Check if current user is a stripe Customer
        customer_list = stripe.Customer.list(email=email).data

        if len(customer_list) == 0:
            # user is not a stripe Customer
            # creating new customer
            customer = stripe.Customer.create(email=email)
        elif len(customer_list) == 1:
            # user is a stripe Customer
            customer = customer_list[0]
        else:
            # multiple users returned
            customer = customer_list[-1]

        # Get all Stripe payment methods for the user
        payment_methods = stripe.PaymentMethod.list(customer=customer.id, type="card", limit=100).data
        if len(payment_methods) == 100:
            next_page = True
            max_loops = 10
            loop = 0
            last_payment_method = payment_methods[-1]
            while next_page and loop < max_loops:
                loop += 1
                new_payment_methods = stripe.PaymentMethod.list(
                    customer=customer.id,
                    type="card",
                    limit=100,
                    starting_after=last_payment_method
                ).data
                if len(new_payment_methods) == 100:
                    payment_methods.extend(new_payment_methods)
                    last_payment_method = new_payment_methods[-1]
                else:
                    next_page = False

        # Dettaching all payment methods
        for payment_method in payment_methods:
            stripe.PaymentMethod.detach(payment_method.id)

        # Attach new payment method to customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer.id,
        )

        # Set as default payment method
        customer.modify(
            customer.id,
            invoice_settings={"default_payment_method": payment_method_id}
        )

        # Check if customer has a subscription
        subscription_list = stripe.Subscription.list(customer=customer.id).data
        if len(subscription_list) == 0:
            # no subscriptions yet
            # creating new subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_id}]
            )
        elif len(subscription_list) == 1:
            # already subscribed
            subscription = subscription_list[0]
            return JsonResponse(
                {
                    'success': False,
                    'message': "You already have an active subscription.",
                    'results': {
                        'customer': customer.id,
                        'subscription': subscription.id,
                    }
                }
            )
        else:
            # multiple subscriptions returned
            subscription = subscription_list[-1]

        return JsonResponse(
            {
                'success': True,
                'message': "You've successfully subscribed!",
                'results': {
                    'customer': customer.id,
                    'subscription': subscription.id,
                }
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):

    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            print(e)
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(e)
            return HttpResponse(status=400)
        print(event['type'])
        if event['type'] == 'customer.subscription.created':
            user = User.objects.get(
                email=stripe.Customer.retrieve(event.data.object.customer).email
            )
            plan = Plan.objects.get(
                product_id=stripe.Price.retrieve(event.data.object['items'].data[0].price.id).product
            )
            subscription, created = Subscription.objects.update_or_create(
                {
                    'plan': plan,
                    'event_id': event.id
                },
                user=user
            )
        elif event['type'] == 'customer.subscription.updated':

            # Check for cancellation updates
            subscription = event.data.object

            # Convert to timezone aware timestamp, based on Stripe timezone configuration
            if subscription.cancel_at:
                cancellation_timestamp = timezone.make_aware(
                    datetime.fromtimestamp(subscription.cancel_at),
                    pytz.timezone(settings.STRIPE_TIMEZONE)
                )
            else:
                cancellation_timestamp = None

            # Update cancellation_timestamp and plan
            user = User.objects.get(
                email=stripe.Customer.retrieve(event.data.object.customer).email
            )
            plan = Plan.objects.get(
                product_id=stripe.Price.retrieve(event.data.object['items'].data[0].price.id).product
            )
            subscription, created = Subscription.objects.update_or_create(
                {
                    'plan': plan,
                    'cancel_at': cancellation_timestamp,
                    'event_id': event.id,
                },
                user=user
            )

        elif event['type'] == 'customer.subscription.deleted':
            user = User.objects.get(
                email=stripe.Customer.retrieve(event.data.object.customer).email
            )
            if Subscription.objects.filter(user=user).exists():
                Subscription.objects.get(user=user).delete()

        return HttpResponse(status=200)


class ConfigurationView(LoginRequiredMixin, TemplateView):

    template_name = "finance/configuration.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Subscription.objects.filter(user=self.request.user).exists():
            context['subscription'] = Subscription.objects.get(user=self.request.user)
        else:
            context['subscription'] = None

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            customer = stripe.Customer.list(email=self.request.user.email).data[0]
            payment_method = stripe.PaymentMethod.retrieve(customer.invoice_settings.default_payment_method)
            context['payment_method'] = payment_method
        except IndexError:
            context['payment_method'] = None

        # For social login controls
        try:
            github_login = self.request.user.social_auth.get(provider='github')
        except UserSocialAuth.DoesNotExist:
            github_login = None

        try:
            twitter_login = self.request.user.social_auth.get(provider='twitter')
        except UserSocialAuth.DoesNotExist:
            twitter_login = None

        try:
            facebook_login = self.request.user.social_auth.get(provider='facebook')
        except UserSocialAuth.DoesNotExist:
            facebook_login = None

        can_disconnect = (self.request.user.social_auth.count() > 1 or self.request.user.has_usable_password())

        context['github_login'] = github_login
        context['twitter_login'] = twitter_login
        context['facebook_login'] = facebook_login
        context['can_disconnect'] = can_disconnect

        return context


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class TransactionViewSet(ModelViewSet):

    queryset = Transaction.objects.order_by('id').all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class ApiMeView(RetrieveAPIView):

    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        return user


class ApiLogoutView(APIView):

    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        Token.objects.get(user=request.user).delete()
        return Response(
            {
                "success": True,
                "message": "Token was successfully deleted.",
            }
        )


class RestrictedAreaView(LoginRequiredMixin, TemplateView):
    template_name = "finance/restricted_area.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(
            is_active=True).exclude(
                id=self.request.user.id)
        return context


class ChartsView(LoginRequiredMixin, TemplateView):
    template_name = "finance/charts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        transactions_by_category = Transaction.objects.filter(
            created_by=self.request.user
        ).values("category__name").annotate(
            sum=Coalesce(Sum("amount"), V(0), output_field=FloatField())
        ).order_by("category__name")
        context['transactions_by_category'] = transactions_by_category

        transactions_by_month_this_year = Transaction.objects.filter(
            created_by=self.request.user,
            timestamp__year=timezone.now().year
        ).values("timestamp__month").annotate(
            sum=Coalesce(Sum("amount"), V(0), output_field=FloatField())
        ).order_by("timestamp__month")
        context['transactions_by_month_this_year'] = transactions_by_month_this_year

        return context
