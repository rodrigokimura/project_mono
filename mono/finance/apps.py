from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model


class FinanceConfig(AppConfig):
    name = 'finance'

    def ready(self):
        from finance.signals import initial_setup, group_initial_setup, installments_creation
        from finance.models import Group, Installment
        User = get_user_model()
        post_save.connect(initial_setup, sender=User, dispatch_uid="user_initial_setup")
        post_save.connect(group_initial_setup, sender=Group, dispatch_uid="group_initial_setup")
        post_save.connect(installments_creation, sender=Installment, dispatch_uid="installments_creation")
