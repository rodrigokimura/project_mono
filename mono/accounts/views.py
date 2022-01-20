import json
import time
from datetime import datetime
from typing import Any

import jwt
import pytz
import stripe
from __mono.mixins import PassRequestToFormViewMixin
from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetCompleteView, PasswordResetConfirmView,
    PasswordResetDoneView, PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import (
    BadRequest, PermissionDenied, SuspiciousOperation,
)
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from rest_framework import authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.models import UserSocialAuth

from .forms import UserForm
from .models import Notification, Plan, Subscription, User, UserProfile
from .serializers import ProfileSerializer, UserSerializer


class SignUp(SuccessMessageMixin, PassRequestToFormViewMixin, CreateView):
    form_class = UserForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy('home')
    success_message = "%(username)s user created successfully"


class Login(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        unread_notifications = self.request.user.notifications.filter(
            read_at__isnull=True
        )
        count = unread_notifications.count()
        if count > 0:
            messages.add_message(
                self.request,
                messages.WARNING,
                f'You have {unread_notifications.count()} unread notification{"s" if count > 1 else ""}.',
            )
        return response


class Logout(LogoutView):
    next_page = reverse_lazy('home')


class PasswordResetView(PasswordResetView):
    success_url = reverse_lazy('finance:password_reset_done')
    title = _('Password reset')
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    template_name = 'registration/password_reset_form.html'
    extra_email_context = {
        "expiration_time_hours": int(settings.PASSWORD_RESET_TIMEOUT / 60 / 60)
    }


class PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('finance:password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'
    title = _('Enter new password')


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'
    title = _('Password reset sent')


class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
    title = _('Password reset complete')


class AccountVerificationView(TemplateView):
    template_name = "finance/invite_acceptance.html"

    def get(self, request):
        token = request.GET.get('t', None)

        if token is None or token == '':
            return HttpResponse("error")

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        user = get_object_or_404(User, pk=payload['user_id'])
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.verify()
        return self.render_to_response({
            "accepted": True,
        })


class LoginAsView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request):
        time.sleep(2)
        user = get_object_or_404(User, id=request.POST.get('user'))
        login(request, user, backend='__mono.auth_backends.EmailOrUsernameModelBackend')
        return JsonResponse(
            {
                "success": True,
                "message": f"Successfully logged in as {user.username}",
            }
        )


class ConfigView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/config.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        up: UserProfile = self.request.user.profile
        if not up.avatar:
            up.generate_initials_avatar()
        context = super().get_context_data(**kwargs)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            customer = stripe.Customer.list(email=self.request.user.email).data[0]
            payment_method = stripe.PaymentMethod.retrieve(customer.invoice_settings.default_payment_method)
            context['payment_method'] = payment_method
        except IndexError:
            context['payment_method'] = None

        notifications = self.request.user.notifications
        context['notifications'] = {
            'unread': notifications.filter(read_at__isnull=True).order_by('-created_at'),
            'read': notifications.filter(read_at__isnull=False).order_by('-created_at'),
        }
        # For social login controls
        try:
            github_login = self.request.user.social_auth.get(provider='github')
        except UserSocialAuth.DoesNotExist:
            github_login = None

        try:
            twitter_login = self.request.user.social_auth.get(provider='twitter')
        except UserSocialAuth.DoesNotExist:
            twitter_login = None

        try:
            facebook_login = self.request.user.social_auth.get(provider='facebook')
        except UserSocialAuth.DoesNotExist:
            facebook_login = None

        can_disconnect = (self.request.user.social_auth.count() > 1 or self.request.user.has_usable_password())

        context['github_login'] = github_login
        context['twitter_login'] = twitter_login
        context['facebook_login'] = facebook_login
        context['can_disconnect'] = can_disconnect
        return context


class UserDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve or update a user instance.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def patch(self, request, pk, format=None, **kwargs):
        user = self.get_object(pk)
        if request.user == user:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('You are trying to edit another user.', status=status.HTTP_403_FORBIDDEN)


class UserProfileDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve or update a user instance.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def patch(self, request, pk, format=None, **kwargs):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if request.user == profile.user:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class NotificationCountView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        qs = self.request.user.notifications.filter(
            read_at__isnull=True
        )
        if qs.exists():
            count = qs.count()
            timestamp = qs.last().created_at.isoformat()
        else:
            count = 0
            timestamp = None
        return JsonResponse({
            'success': True,
            'count': count,
            'timestamp': timestamp,
        })


class NotificationActionView(LoginRequiredMixin, SingleObjectMixin, View):

    model = Notification

    def get(self, *args, **kwargs):

        notification = self.get_object()
        if not notification.to == self.request.user:
            raise PermissionDenied
        if not notification.read:
            notification.mark_as_read()
            messages.add_message(
                self.request,
                messages.SUCCESS,
                'Notification marked as read.',
            )
        if notification.action_url:
            return redirect(notification.action_url)
        return redirect('/')


class MarkNotificationsAsReadView(LoginRequiredMixin, View):

    def post(self, request):
        ids = json.loads(request.POST.get('ids', ''))

        if len(ids) == 0:
            raise BadRequest('No notification ids were passed.')

        for id in ids:
            n = Notification.objects.get(id=int(id))
            if n.to == request.user:
                n.mark_as_read()

        messages.add_message(
            request,
            messages.SUCCESS,
            f'You marked {len(ids)} notification{"s" if len(ids) > 1 else ""} as read.',
        )
        return JsonResponse({
            'success': True,
            'data': ids
        })


class MarkNotificationsAsUnreadView(LoginRequiredMixin, View):

    def post(self, request):
        ids = json.loads(request.POST.get('ids', ''))
        for id in ids:
            n = Notification.objects.get(id=int(id))
            if n.to == request.user:
                n.mark_as_unread()
        messages.add_message(
            request,
            messages.SUCCESS,
            f'You marked {len(ids)} notification{"s" if len(ids) > 1 else ""} as unread.',
        )
        return JsonResponse({
            'success': True,
            'data': ids
        })


class ApiMeView(RetrieveAPIView):

    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        return user


class ApiLogoutView(APIView):

    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        Token.objects.get(user=request.user).delete()
        return Response(
            {
                "success": True,
                "message": "Token was successfully deleted.",
            }
        )


class PlansView(UserPassesTestMixin, TemplateView):
    template_name = "finance/plans.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Get all Stripe products
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

        # Filter products by metada {app:finance}
        products = filter(lambda product: hasattr(product.metadata, 'app'), products)
        products = [product for product in products if product.metadata.app == 'finance']

        # Sort products according to business rules
        pass

        context['plans'] = Plan.objects.filter(product_id__in=[product.id for product in products])
        context['free_plan'] = Plan.objects.filter(
            product_id__in=[product.id for product in products],
            type=Plan.FREE
        ).first()
        if self.request.user.is_authenticated:
            if Subscription.objects.filter(user=self.request.user).exists():
                user_plan = Subscription.objects.get(user=self.request.user).plan
            else:
                user_plan = Plan.objects.get(type=Plan.FREE)
        else:
            user_plan = None
        context['user_plan'] = user_plan

        return context


class CheckoutView(UserPassesTestMixin, TemplateView):
    template_name = "finance/checkout.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_pk'] = settings.STRIPE_PUBLIC_KEY
        # Check query param 'plan'
        plan_id = self.request.GET.get("plan", None)
        if plan_id not in ["", None]:
            plan = get_object_or_404(Plan, pk=plan_id)
            context['plan'] = plan
        else:
            raise SuspiciousOperation("Invalid request. This route need a query parameter 'plan'.")

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            product = stripe.Product.retrieve(plan.product_id)
            context['product'] = product
        except Exception as e:
            print(e)
            raise SuspiciousOperation(e)

        # Get currency from language
        if self.request.LANGUAGE_CODE == 'pt-br':
            currency = 'brl'
        else:
            currency = 'usd'

        # Get Plans for the plan
        plans = stripe.Plan.list(product=product.id, active=True, currency=currency).data

        # Get monthly plan price
        plans_for_context = []
        try:
            monthly_price = list(filter(lambda price: price.interval == 'month', plans))[0]
            plans_for_context.append(monthly_price)
        except Exception as e:
            print(e)

        # Get yearly plan price
        try:
            yearly_price = list(filter(lambda price: price.interval == 'year', plans))[0]
            plans_for_context.append(yearly_price)
        except Exception as e:
            print(e)

        context['plans'] = plans_for_context

        return context

    def get(self, request):
        plan_id = self.request.GET.get("plan", None)
        plan = get_object_or_404(Plan, pk=plan_id)
        if plan.type == Plan.FREE:
            if Subscription.objects.filter(user=request.user).exists():
                subscription = Subscription.objects.get(user=request.user)

                (success, message) = subscription.cancel_at_period_end()
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)
                return redirect(to=reverse('accounts:plans'))
            else:
                messages.error(request, "You are already subscribed to the Free Plan.")
                return redirect(to=reverse('accounts:plans'))
        else:
            return self.render_to_response(self.get_context_data())

    def post(self, request):
        payment_method_id = request.POST.get("payment_method_id")
        price_id = request.POST.get("price_id")

        stripe.api_key = settings.STRIPE_SECRET_KEY

        email = self.request.user.email

        # Check if current user is a stripe Customer
        customer_list = stripe.Customer.list(email=email).data

        if len(customer_list) == 0:
            # user is not a stripe Customer
            # creating new customer
            customer = stripe.Customer.create(email=email)
        elif len(customer_list) == 1:
            # user is a stripe Customer
            customer = customer_list[0]
        else:
            # multiple users returned
            customer = customer_list[-1]

        # Get all Stripe payment methods for the user
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

        # Dettaching all payment methods
        for payment_method in payment_methods:
            stripe.PaymentMethod.detach(payment_method.id)

        # Attach new payment method to customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer.id,
        )

        # Set as default payment method
        customer.modify(
            customer.id,
            invoice_settings={"default_payment_method": payment_method_id}
        )

        # Check if customer has a subscription
        subscription_list = stripe.Subscription.list(customer=customer.id).data
        if len(subscription_list) == 0:
            # no subscriptions yet
            # creating new subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_id}]
            )
        elif len(subscription_list) == 1:
            # already subscribed
            subscription = subscription_list[0]
            return JsonResponse(
                {
                    'success': False,
                    'message': "You already have an active subscription.",
                    'results': {
                        'customer': customer.id,
                        'subscription': subscription.id,
                    }
                }
            )
        else:
            # multiple subscriptions returned
            subscription = subscription_list[-1]

        return JsonResponse(
            {
                'success': True,
                'message': "You've successfully subscribed!",
                'results': {
                    'customer': customer.id,
                    'subscription': subscription.id,
                }
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):

    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            print(e)
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(e)
            return HttpResponse(status=400)
        print(event['type'])
        if event['type'] == 'customer.subscription.created':
            user = User.objects.get(
                email=stripe.Customer.retrieve(event.data.object.customer).email
            )
            plan = Plan.objects.get(
                product_id=stripe.Price.retrieve(event.data.object['items'].data[0].price.id).product
            )
            subscription, created = Subscription.objects.update_or_create(
                {
                    'plan': plan,
                    'event_id': event.id
                },
                user=user
            )
        elif event['type'] == 'customer.subscription.updated':

            # Check for cancellation updates
            subscription = event.data.object

            # Convert to timezone aware timestamp, based on Stripe timezone configuration
            if subscription.cancel_at:
                cancellation_timestamp = timezone.make_aware(
                    datetime.fromtimestamp(subscription.cancel_at),
                    pytz.timezone(settings.STRIPE_TIMEZONE)
                )
            else:
                cancellation_timestamp = None

            # Update cancellation_timestamp and plan
            user = User.objects.get(
                email=stripe.Customer.retrieve(event.data.object.customer).email
            )
            plan = Plan.objects.get(
                product_id=stripe.Price.retrieve(event.data.object['items'].data[0].price.id).product
            )
            subscription, created = Subscription.objects.update_or_create(
                {
                    'plan': plan,
                    'cancel_at': cancellation_timestamp,
                    'event_id': event.id,
                },
                user=user
            )

        elif event['type'] == 'customer.subscription.deleted':
            user = User.objects.get(
                email=stripe.Customer.retrieve(event.data.object.customer).email
            )
            if Subscription.objects.filter(user=user).exists():
                Subscription.objects.get(user=user).delete()

        return HttpResponse(status=200)
