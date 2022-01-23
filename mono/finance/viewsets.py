"""Finance's viewsets"""
from rest_framework.viewsets import ModelViewSet

from .models import (
    Account, Category, Installment, RecurrentTransaction, Transaction,
    Transference, User
)
from .permissions import IsCreator
from .serializers import (
    AccountSerializer, CategorySerializer, InstallmentSerializer,
    RecurrentTransactionSerializer, TransactionSerializer,
    TransferenceSerializer, UserSerializer,
)
# pylint: disable=R0901


class UserViewSet(ModelViewSet):
    """User viewset"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class CategoryViewSet(ModelViewSet):
    """Category viewset"""

    queryset = Category.objects.order_by('id').all()
    serializer_class = CategorySerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            created_by=self.request.user,
            internal_type=Category.DEFAULT,
        )


class AccountViewSet(ModelViewSet):
    """Account viewset"""

    queryset = Account.objects.order_by('id').all()
    serializer_class = AccountSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class TransactionViewSet(ModelViewSet):
    """Transaction viewset"""

    queryset = Transaction.objects.order_by('id').all()
    serializer_class = TransactionSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class RecurrentTransactionViewSet(ModelViewSet):
    """Recurrent transaction viewset"""

    queryset = RecurrentTransaction.objects.order_by('id').all()
    serializer_class = RecurrentTransactionSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class InstallmentViewSet(ModelViewSet):
    """Installment viewset"""

    queryset = Installment.objects.order_by('id').all()
    serializer_class = InstallmentSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class TransferenceViewSet(ModelViewSet):
    """Transference viewset"""

    queryset = Transference.objects.order_by('id').all()
    serializer_class = TransferenceSerializer
    permission_classes = [IsCreator]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)
