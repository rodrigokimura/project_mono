from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save


class HealthcheckConfig(AppConfig):
    name = 'healthcheck'

    def ready(self):
        from accounts.signals import email_verification
        from finance.models import (
            Group, Installment, Transaction, Transference,
        )
        from finance.signals import (
            group_initial_setup, initial_setup, installments_creation,
            round_transaction, transference_creation,
        )
        User = get_user_model()
        post_save.connect(initial_setup, sender=User, dispatch_uid="user_initial_setup")
        post_save.connect(group_initial_setup, sender=Group, dispatch_uid="group_initial_setup")
        post_save.connect(installments_creation, sender=Installment, dispatch_uid="installments_creation")
        post_save.connect(transference_creation, sender=Transference, dispatch_uid="transference_creation")
        post_save.connect(email_verification, sender=User, dispatch_uid="email_verification")
        pre_save.connect(round_transaction, sender=Transaction, dispatch_uid="round_transaction")
