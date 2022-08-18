"""Command to sync subscriptions from Stripe"""
from datetime import datetime

import pytz
import stripe
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...models import Plan, Subscription, User
from ...stripe import get_all_customers


class Command(BaseCommand):
    help = "Command to sync subscriptions from Stripe"

    def handle(self, *args, **options):
        """Command to sync subscriptions from Stripe"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Get all Stripe customers
            customers = get_all_customers()

            # Get subscription for each customer
            # Assumes one to one
            for customer in customers:
                print(f"Fetching customer {customer.id}")

                subscriptions = stripe.Subscription.list(
                    customer=customer.id
                ).data

                if len(subscriptions) > 0:
                    stripe_subscription = stripe.Subscription.list(
                        customer=customer.id
                    ).data[0]
                    stripe_plan = Plan.objects.get(
                        product_id=stripe_subscription["items"]
                        .data[0]
                        .price.product
                    )
                    if stripe_subscription.cancel_at is not None:
                        stripe_cancel_at = timezone.make_aware(
                            datetime.fromtimestamp(
                                stripe_subscription.cancel_at
                            ),
                            pytz.timezone(settings.STRIPE_TIMEZONE),
                        )
                    else:
                        stripe_cancel_at = None

                    if Subscription.objects.filter(
                        user=User.objects.get(email=customer.email)
                    ).exists():
                        user_subscription = Subscription.objects.get(
                            user=User.objects.get(email=customer.email)
                        )
                        # If subscription is not the one stored,
                        # updates the user's subscription
                        if (
                            user_subscription.plan,
                            user_subscription.cancel_at,
                        ) != (
                            stripe_plan,
                            stripe_cancel_at,
                        ):
                            print(f"Updating customer {customer.id}")
                            user_subscription.plan = stripe_plan
                            user_subscription.cancel_at = stripe_cancel_at
                            user_subscription.save()
                        else:
                            print("No changes to apply.")
                    else:
                        Subscription.objects.create(
                            user=User.objects.get(email=customer.email),
                            plan=stripe_plan,
                            cancel_at=stripe_cancel_at,
                        )
                        print("Subscription created.")
                else:
                    if Subscription.objects.filter(
                        user=User.objects.get(email=customer.email)
                    ).exists():
                        Subscription.objects.get(
                            user=User.objects.get(email=customer.email)
                        ).delete()
                        print(f"Updating customer {customer.id}")
                    else:
                        print(
                            f"Customer {customer.id} has no subscriptions (FREE PLAN)."
                        )
        except Exception as any_exception:  # pylint: disable=broad-except
            raise CommandError(repr(any_exception)) from any_exception
