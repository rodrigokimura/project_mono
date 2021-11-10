from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

from .models import (
    Account, Category, Installment, RecurrentTransaction, Transaction,
)
from .serializers import (
    AccountSerializer, CategorySerializer, InstallmentSerializer,
    RecurrentTransactionSerializer, TransactionSerializer, UserSerializer,
)


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class CategoryViewSet(ModelViewSet):

    queryset = Category.objects.order_by('id').all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            created_by=self.request.user,
            internal_type=Category.DEFAULT,
        )


class AccountViewSet(ModelViewSet):

    queryset = Account.objects.order_by('id').all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class TransactionViewSet(ModelViewSet):

    queryset = Transaction.objects.order_by('id').all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class RecurrentTransactionViewSet(ModelViewSet):

    queryset = RecurrentTransaction.objects.order_by('id').all()
    serializer_class = RecurrentTransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class InstallmentViewSet(ModelViewSet):

    queryset = Installment.objects.order_by('id').all()
    serializer_class = InstallmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)
