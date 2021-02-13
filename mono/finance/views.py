from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView


# Create your views here.

from .models import Transaction

def index(request):
  return render(request, 'finance/index.html', {})

def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    return render(request, 'finance/transaction_detail.html', {'transaction': transaction})