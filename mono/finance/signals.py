from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from .models import (
    Account, Category, Configuration, Group, Icon, Installment, Transaction,
    Transference, User,
)


@receiver(post_save, sender=User, dispatch_uid="initial_setup")
def initial_setup(sender, instance, created, **kwargs):
    if created and sender == User:
        # Initial accounts
        Account.objects.get_or_create(name="Wallet", owned_by=instance, created_by=instance)
        Account.objects.get_or_create(name="Bank", owned_by=instance, created_by=instance)

        # Initial categories
        for category in Category.INITIAL_CATEGORIES:
            Category.objects.get_or_create(
                name=category[0],
                type=category[1],
                icon=Icon.objects.get(markup=category[2]),
                created_by=instance,
            )
        for category in Category.SPECIAL_CATEGORIES:
            Category.objects.get_or_create(
                name=category[0],
                type=category[1],
                icon=Icon.objects.get(markup=category[2]),
                internal_type=category[3],
                created_by=instance,
            )

        # Initial configuration
        config, created = Configuration.objects.get_or_create(user=instance)
        config.cards = '1,2,3'
        config.save()


@receiver(post_save, sender=Group, dispatch_uid="group_initial_setup")
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


@receiver(post_save, sender=Installment, dispatch_uid="installments_creation")
def installments_creation(sender, instance, created, **kwargs):
    if sender == Installment:
        if created:
            instance.create_transactions()
        else:
            transactions = Transaction.objects.filter(installment=instance)
            for transaction in transactions:
                transaction.delete()
            instance.create_transactions()


@receiver(post_save, sender=Transference, dispatch_uid="transference_creation")
def transference_creation(sender, instance, created, **kwargs):
    if sender == Transference:
        if created:
            instance.create_transactions()
        else:
            transactions = Transaction.objects.filter(transference=instance)
            for transaction in transactions:
                transaction.delete()
            instance.create_transactions()


@receiver(pre_save, sender=Transaction, dispatch_uid="round_transaction")
def round_transaction(sender, instance, **kwargs):
    if sender == Transaction:
        instance.round_amount()
