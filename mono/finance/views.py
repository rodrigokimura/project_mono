from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.db.models.functions import Coalesce

# Create your views here.

from .models import Transaction, Category, Account
from .forms import TransactionForm
from django.db.models.functions import TruncDay
from django.db.models import Sum

def index(request):
  return render(request, 'finance/index.html', {})

def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    return render(request, 'finance/transaction_detail.html', {'transaction': transaction})

class TransactionListView(ListView):
    model = Transaction
    paginate_by = 100
    
    def get_queryset(self):
        category = self.request.GET.get('category', None)
        qs = Transaction.objects.all()
        qs = qs.annotate(date=TruncDay('timestamp'))
        qs = qs.order_by('-timestamp')
        
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

class TransactionCreateView(SuccessMessageMixin, CreateView): 
    model = Transaction 
    form_class = TransactionForm
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was created successfully"

class TransactionUpdateView(SuccessMessageMixin, UpdateView): 
    model = Transaction 
    form_class = TransactionForm
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was updated successfully"
  
class TransactionDeleteView(SuccessMessageMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy('finance:transactions')
    success_message = "Transaction was deleted successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(TransactionDeleteView, self).delete(request, *args, **kwargs)
        

class AccountListView(ListView):
    model = Account