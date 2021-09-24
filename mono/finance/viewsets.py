from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

from .models import Transaction
from .serializers import TransactionSerializer, UserSerializer


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class TransactionViewSet(ModelViewSet):

    queryset = Transaction.objects.order_by('id').all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)
