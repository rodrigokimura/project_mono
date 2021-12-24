from django.contrib.auth.models import User
from rest_framework import fields, serializers

from .models import (
    Account, Category, Chart, Icon, Installment, RecurrentTransaction,
    Transaction, Transference,
)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class AccountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Account.objects.all())

    class Meta:
        model = Account
        fields = [
            'url',
            "id",
            "name",
            "created_by",
            "owned_by",
            "group",
            "initial_balance",
            "credit_card",
            "settlement_date",
            "due_date"
        ]
        read_only_fields = [
            'url',
            "name",
            "created_by",
            "owned_by",
            "group",
            "initial_balance",
            "credit_card",
            "settlement_date",
            "due_date"
        ]


class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icon
        fields = [
            "markup",
        ]


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Category.objects.all())
    icon = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "url",
            "id",
            "name",
            "description",
            "type",
            "created_by",
            "created_at",
            "group",
            "icon",
            "active"
        ]
        read_only_fields = [
            "url",
            "name",
            "description",
            "type",
            "created_by",
            "created_at",
            "group",
            "icon",
            "active"
        ]


class TransactionSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = CategorySerializer()
    account = AccountSerializer()

    class Meta:
        model = Transaction
        fields = [
            'url',
            'description',
            'account',
            'category',
            'created_by',
            'timestamp',
            'amount',
        ]
        read_only_fields = []
        depth = 1

    def create(self, validated_data):
        transaction = Transaction.objects.create(
            account=validated_data.pop('account')['id'],
            category=validated_data.pop('category')['id'],
            **validated_data,
        )
        return transaction

    def update(self, instance, validated_data):
        instance.account = validated_data.pop('account')['id']
        instance.category = validated_data.pop('category')['id']
        instance = super().update(instance, validated_data)
        return instance


class RecurrentTransactionSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = CategorySerializer()
    account = AccountSerializer()

    class Meta:
        model = RecurrentTransaction
        fields = [
            'url',
            'description',
            'account',
            'category',
            'created_by',
            'timestamp',
            'amount',
            'frequency',
        ]
        read_only_fields = []
        depth = 1

    def create(self, validated_data):
        transaction = RecurrentTransaction.objects.create(
            account=validated_data.pop('account')['id'],
            category=validated_data.pop('category')['id'],
            **validated_data,
        )
        return transaction

    def update(self, instance, validated_data):
        instance.account = validated_data.pop('account')['id']
        instance.category = validated_data.pop('category')['id']
        instance = super().update(instance, validated_data)
        return instance


class InstallmentSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = CategorySerializer()
    account = AccountSerializer()

    class Meta:
        model = Installment
        fields = [
            'url',
            'description',
            'account',
            'category',
            'created_by',
            'timestamp',
            'total_amount',
            'months',
            'handle_remainder',
        ]
        read_only_fields = []
        depth = 1

    def create(self, validated_data):
        transaction = Installment.objects.create(
            account=validated_data.pop('account')['id'],
            category=validated_data.pop('category')['id'],
            **validated_data,
        )
        return transaction

    def update(self, instance, validated_data):
        instance.account = validated_data.pop('account')['id']
        instance.category = validated_data.pop('category')['id']
        instance = super().update(instance, validated_data)
        return instance


class TransferenceSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    from_account = AccountSerializer()
    to_account = AccountSerializer()

    def validate(self, data):
        if data['from_account'] == data['to_account']:
            raise serializers.ValidationError('Accounts must be different')
        return data

    class Meta:
        model = Transference
        fields = [
            'url',
            'description',
            'to_account',
            'from_account',
            'created_by',
            'timestamp',
            'amount',
        ]
        read_only_fields = []
        depth = 1

    def create(self, validated_data):
        transaction = Transference.objects.create(
            from_account=validated_data.pop('from_account')['id'],
            to_account=validated_data.pop('to_account')['id'],
            **validated_data,
        )
        return transaction


class ChartSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    filters = fields.MultipleChoiceField(choices=Chart.FILTER_CHOICES)

    class Meta:
        model = Chart
        fields = [
            "type",
            "metric",
            "field",
            "axis",
            "category",
            "filters",
            "created_by",
            "created_at",
            "updated_at",
            "title",
            "order",
        ]
