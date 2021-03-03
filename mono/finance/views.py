from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce, TruncDay
from .models import Transaction, Category, Account, Group, Category, Icon, Goal, Invite
from .forms import TransactionForm, GroupForm, CategoryForm, UserForm, AccountForm, IconForm, GoalForm
import time
import jwt

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

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    paginate_by = 100
    
    def get_queryset(self):
        category = self.request.GET.get('category', None)
        qs = Transaction.objects.all()
        qs = qs.annotate(date=TruncDay('timestamp'))
        qs = qs.order_by('-timestamp')
        qs = qs.filter(created_by=self.request.user)
        
        if category not in [None, ""]:
            qs = qs.filter(category=category)
            
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['categories'] = Category.objects.all()
        qs = self.get_queryset()
        qs = qs.annotate(date=TruncDay('timestamp')).values('date')
        qs = qs.annotate(
            total_expense=Coalesce(
                Sum(
                  'ammount', 
                  filter=Q(type='EXP')
                ), 0
            )
        )
        qs = qs.annotate(
            total_income=Coalesce(
                Sum(
                    'ammount', 
                    filter=Q(type='INC')
                ), 0
            )
        )
        qs = qs.order_by('-date')
        
        context['dates'] = qs
        
        return context

class TransactionCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView): 
    model = Transaction 
    form_class = TransactionForm
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was created successfully"

class TransactionUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView): 
    model = Transaction 
    form_class = TransactionForm
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was updated successfully"
  
class TransactionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy('finance:transactions')
    success_message = "Transaction was deleted successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(TransactionDeleteView, self).delete(request, *args, **kwargs)

class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    
    def get_queryset(self):
        qs = Account.objects.filter(belongs_to=self.request.user)
        return qs
    
class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account

class AccountCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView): 
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('finance:accounts')
    success_message = "%(name)s was created successfully"

class AccountUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView): 
    model = Account 
    form_class = AccountForm
    success_url = reverse_lazy('finance:accounts')
    success_message = "%(name)s was updated successfully"
  
class AccountDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Account
    success_url = reverse_lazy('finance:accounts')
    success_message = "Account was deleted successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(AccountDeleteView, self).delete(request, *args, **kwargs)

class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    
    def get_queryset(self):
        qs = Group.objects.all()
        qs = qs.filter(members__in=[self.request.user])
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
    

class GroupDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('finance:groups')
    success_message = "Group was deleted successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(GroupDeleteView, self).delete(request, *args, **kwargs)
        
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category 
    
    def get_queryset(self):
        qs = Category.objects.all()
        qs = qs.filter(created_by=self.request.user)
        return qs
        
class CategoryListApi(View):
    def get(self, request):
        type = request.GET.get("type", "EXP")
        account = request.GET.get("account")
        qs = Category.objects.all()
        qs = qs.filter(created_by=request.user)
        qs = qs.filter(type=type)
        qs = qs.values('name')
        qs = qs.annotate(value=F('id'))
        qs = qs.annotate(icon=F('icon__markup'))
        return JsonResponse(
            {
                'success':True,
                'message':'Categories retrived from database.',
                'results':list(qs),
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
    
class CategoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('finance:categories')
    success_message = "Category was deleted successfully"

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
        
        if Invite.objects.filter(email=email,group=group).exists():
            response = {
                'success': True,
                'message':f"You've already invited {email} to this group."
            }
        elif email == '':
            response = {
                'success': False,
                'message':'Email cannot be empty.'
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
                'success':True,
                'message':'Invite created.',
                'results':invite.pk,
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
        
        qs = Invite.objects.filter(group=group)
        qs = qs.values('email','accepted')
        
        if qs.count() == 0:
            response = {
                'success':True,
                'message':"No invites found.",
                'results': None
            }
            print('zero')
        else:
            response = {
                'success':True,
                'message':"List of invites.",
                'results':list(qs)
            }
        return JsonResponse(response)
    
class InviteAcceptionView(TokenMixin, LoginRequiredMixin, View):
    
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
            
            accepted = invite.accepted
            user_already_member = request.user in invite.group.members.all()
            if not accepted and not user_already_member:
                invite.accept(request.user)
                invite.save()
            
            return HttpResponse(invite.accepted)