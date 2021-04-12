from rest_framework.serializers import HyperlinkedModelSerializer
from django.contrib.auth.models import User
from .models import Transaction

class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class TransactionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'url',
            'description',
            'created_by',
            'created_at',
            'timestamp',
            'amount',
        ]