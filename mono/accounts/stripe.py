"""Handle stripe operations"""
from typing import List, Tuple

import stripe


def get_or_create_customer(email: str) -> Tuple[stripe.Customer, bool]:
    """Check if a stripe Customer exists for the given email."""
    customers = stripe.Customer.list(email=email).data
    if len(customers) == 0:
        return stripe.Customer.create(email=email), True
    if len(customers) == 1:
        return customers[0], False
    return customers[-1], False


def get_payment_methods(customer: stripe.Customer) -> List[stripe.PaymentMethod]:
    """Return a list of payment methods for the given customer."""
    payment_methods = stripe.PaymentMethod.list(customer=customer.id, type="card", limit=100).data
    if len(payment_methods) == 100:
        next_page = True
        max_loops = 10
        loop = 0
        last_payment_method = payment_methods[-1]
        while next_page and loop < max_loops:
            loop += 1
            new_payment_methods = stripe.PaymentMethod.list(
                customer=customer.id,
                type="card",
                limit=100,
                starting_after=last_payment_method
            ).data
            if len(new_payment_methods) == 100:
                payment_methods.extend(new_payment_methods)
                last_payment_method = new_payment_methods[-1]
            else:
                next_page = False
    return payment_methods


def get_or_create_subscription(customer: stripe.Customer, price_id: str) -> Tuple[stripe.Subscription, bool]:
    """Check if customer has a subscription"""
    subscriptions = stripe.Subscription.list(customer=customer.id).data
    if len(subscriptions) == 0:
        return stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": price_id}]
        ), True
    if len(subscriptions) == 1:
        return subscriptions[0], False
    return subscriptions[-1], False


def get_products():
    """Get all Stripe products"""
    products = stripe.Product.list(limit=100, active=True).data
    if len(products) == 100:
        next_page = True
        max_loops = 10
        loop = 0
        last_product = products[-1]
        while next_page and loop < max_loops:
            loop += 1
            new_products = stripe.Product.list(limit=100, starting_after=last_product).data
            if len(new_products) == 100:
                products.extend(new_products)
                last_product = new_products[-1]
            else:
                next_page = False

    return products
