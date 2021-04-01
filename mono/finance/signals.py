from .models import Configuration, Account, Category, Group, Icon, Installment, Transaction, User


def initial_setup(sender, instance, created, **kwargs):
    if created and sender == User:
        # Initial accounts
        Account.objects.create(name="Wallet", owned_by=instance, created_by=instance)
        Account.objects.create(name="Bank", owned_by=instance, created_by=instance)

        # Initial categories
        for category in Category.INITIAL_CATEGORIES:
            Category.objects.create(
                name=category[0],
                type=category[1],
                icon=Icon.objects.get(markup=category[2]),
                created_by=instance,
            )
        for category in Category.SPECIAL_CATEGORIES:
            Category.objects.create(
                name=category[0],
                type=category[1],
                icon=Icon.objects.get(markup=category[2]),
                internal_type=category[3],
                created_by=instance,
            )

        # Initial configuration
        Configuration.objects.create(user=instance)


def group_initial_setup(sender, instance, created, **kwargs):
    if created and sender == Group:
        # Initial categories for the group
        for category in Category.INITIAL_CATEGORIES:
            Category.objects.create(
                name=category[0],
                type=category[1],
                icon=Icon.objects.get(markup=category[2]),
                created_by=instance.created_by,
                group=instance,
            )
        for category in Category.SPECIAL_CATEGORIES:
            Category.objects.create(
                name=category[0],
                type=category[1],
                icon=Icon.objects.get(markup=category[2]),
                internal_type=category[3],
                created_by=instance.created_by,
                group=instance,
            )


def installments_creation(sender, instance, created, **kwargs):
    if sender == Installment:
        if created:
            instance.create_transactions()
        else:
            transactions = Transaction.objects.filter(installment=instance)
            for transaction in transactions:
                transaction.delete()
            instance.create_transactions()
