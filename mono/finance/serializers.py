"""Finance's serializers"""
from rest_framework import fields, serializers

from .models import (
    Account,
    Category,
    Chart,
    Icon,
    Installment,
    RecurrentTransaction,
    Transaction,
    Transference,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    class Meta:
        model = User
        fields = ["username", "email", "is_staff"]


class AccountSerializer(serializers.ModelSerializer):
    """Account serializer"""

    id = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Account.objects.all()
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "created_by",
            "owned_by",
            "group",
            "initial_balance",
            "credit_card",
            "settlement_date",
            "due_date",
        ]
        read_only_fields = [
            "name",
            "created_by",
            "owned_by",
            "group",
            "initial_balance",
            "credit_card",
            "settlement_date",
            "due_date",
        ]


class IconSerializer(serializers.ModelSerializer):
    """Icon serializer"""

    class Meta:
        model = Icon
        fields = [
            "markup",
        ]


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""

    id = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Category.objects.all()
    )
    icon = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "type",
            "created_by",
            "created_at",
            "group",
            "icon",
            "active",
        ]
        read_only_fields = [
            "name",
            "description",
            "type",
            "created_by",
            "created_at",
            "group",
            "icon",
            "active",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = CategorySerializer()
    account = AccountSerializer()

    class Meta:
        model = Transaction
        fields = [
            "description",
            "account",
            "category",
            "created_by",
            "timestamp",
            "amount",
        ]
        read_only_fields = []
        depth = 1

    def create(self, validated_data):
        transaction = Transaction.objects.create(
            account=validated_data.pop("account")["id"],
            category=validated_data.pop("category")["id"],
            **validated_data,
        )
        return transaction

    def update(self, instance, validated_data):
        instance.account = validated_data.pop("account")["id"]
        instance.category = validated_data.pop("category")["id"]
        instance = super().update(instance, validated_data)
        return instance


class RecurrentTransactionSerializer(serializers.ModelSerializer):
    """Recurrent transaction serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = CategorySerializer()
    account = AccountSerializer()

    class Meta:
        model = RecurrentTransaction
        fields = [
            "description",
            "account",
            "category",
            "created_by",
            "timestamp",
            "amount",
            "frequency",
        ]
        read_only_fields = []
        depth = 1

    def create(self, validated_data):
        transaction = RecurrentTransaction.objects.create(
            account=validated_data.pop("account")["id"],
            category=validated_data.pop("category")["id"],
            **validated_data,
        )
        return transaction

    def update(self, instance, validated_data):
        instance.account = validated_data.pop("account")["id"]
        instance.category = validated_data.pop("category")["id"]
        instance = super().update(instance, validated_data)
        return instance


class InstallmentSerializer(serializers.ModelSerializer):
    """Installment serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = CategorySerializer()
    account = AccountSerializer()

    class Meta:
        model = Installment
        fields = [
            "description",
            "account",
            "category",
            "created_by",
            "timestamp",
            "total_amount",
            "months",
            "handle_remainder",
        ]
        read_only_fields = []
        depth = 1

    def create(self, validated_data):
        transaction = Installment.objects.create(
            account=validated_data.pop("account")["id"],
            category=validated_data.pop("category")["id"],
            **validated_data,
        )
        return transaction

    def update(self, instance, validated_data):
        instance.account = validated_data.pop("account")["id"]
        instance.category = validated_data.pop("category")["id"]
        instance = super().update(instance, validated_data)
        return instance


class TransferenceSerializer(serializers.ModelSerializer):
    """Transference serializer"""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    from_account = AccountSerializer()
    to_account = AccountSerializer()

    def validate(self, attrs):
        if attrs["from_account"] == attrs["to_account"]:
            raise serializers.ValidationError("Accounts must be different")
        return attrs

    class Meta:
        model = Transference
        fields = [
            "description",
            "to_account",
            "from_account",
            "created_by",
            "timestamp",
            "amount",
        ]
        read_only_fields = []
        depth = 1

    def create(self, validated_data):
        transaction = Transference.objects.create(
            from_account=validated_data.pop("from_account")["id"],
            to_account=validated_data.pop("to_account")["id"],
            **validated_data,
        )
        return transaction


class ChartSerializer(serializers.ModelSerializer):
    """Chart serializer"""

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


class ChartMoveSerializer(serializers.Serializer):
    """Apply chart movement"""

    order = serializers.IntegerField()
    chart = serializers.IntegerField()

    def validate_chart(self, value):
        """Chart must exist"""
        if Chart.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Invalid chart")

    def validate_order(self, value):
        """Order must be positive"""
        if value > 0:
            return value
        raise serializers.ValidationError("Invalid order")

    def _change_other_charts_order(self, order):
        """Fix other charts order"""
        other_charts = self.context["request"].user.charts.exclude(
            id=self.validated_data["chart"]
        )
        for i, chart in enumerate(other_charts):
            if i + 1 < order:
                chart.order = i + 1
                chart.save()
            else:
                chart.order = i + 2
                chart.save()

    def move(self):
        """Apply chart movement"""
        chart = Chart.objects.get(id=self.validated_data["chart"])
        order = self.validated_data["order"]
        self._change_other_charts_order(order)
        chart.order = order
        chart.save()
        return {"success": True}

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
