from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

# Create your views here.

from .models import Transaction, Category 
from .forms import TransactionForm

def index(request):
  return render(request, 'finance/index.html', {})

def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    return render(request, 'finance/transaction_detail.html', {'transaction': transaction})

class TransactionFormView(FormView):
    form_class = TransactionForm
    template_name = 'finance/transaction_form.html'
    success_url = '/fn'
    
def transaction(request):
    template = "finance/transaction_form.html"
    if request.method == "POST":
        form = TransactionForm(data = request.POST)
        if form.is_valid():
            form.save()
        else:
            for field in form.errors:
                form[field].field.widget.attrs.update({'class': 'field error'})
    elif request.method == "GET":
        form = TransactionForm()

    return render(request, template, {
        "form":form,
    })
    
class TransactionListView(ListView):

    model = Transaction
    paginate_by = 100
    
    def get_queryset(self):
        category = self.request.GET.get('category', None)
        qs = Transaction.objects.all()
        if category not in [None, ""]:
            qs = qs.filter(category=category)
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['categories'] = Category.objects.all()
        return context
        

class TransactionCreateView(SuccessMessageMixin, CreateView): 
    model = Transaction 
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was created successfully"
    fields = [
      'description',
      'category',
      'created_by',
      'value',
      'account',
      'category',
    ]

class TransactionUpdateView(SuccessMessageMixin, UpdateView): 
    model = Transaction 
    success_url = reverse_lazy('finance:transactions')
    success_message = "%(description)s was updated successfully"
    fields = [
      'description',
      'category',
      'created_by',
      'value',
      'account',
      'category',
    ]
  
class TransactionDeleteView(SuccessMessageMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy('finance:transactions')
    success_message = "Transaction was deleted successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(TransactionDeleteView, self).delete(request, *args, **kwargs)