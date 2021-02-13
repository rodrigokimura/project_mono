from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView


# Create your views here.

from .models import Transaction
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