"""Account's views."""
import json
from datetime import datetime

import jwt
import pytz
import stripe
from __mono.mixins import PassRequestToFormViewMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetCompleteView as _PasswordResetCompleteView,
    PasswordResetConfirmView as _PasswordResetConfirmView,
    PasswordResetDoneView as _PasswordResetDoneView,
    PasswordResetView as _PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import BadRequest, PermissionDenied
from django.db.models import QuerySet
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from rest_framework import authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.models import UserSocialAuth

from .forms import UserForm
from .models import Notification, Plan, Subscription, User, UserProfile
from .serializers import (
    ChangePasswordSerializer, ProfileSerializer, UserSerializer,
)
from .stripe import (
    get_or_create_customer, get_or_create_subscription, get_payment_methods,
    get_products,
)


class SignUp(SuccessMessageMixin, PassRequestToFormViewMixin, CreateView):
    """
    Sign up view.
    """
    form_class = UserForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy('home')
    success_message = "%(username)s user created successfully"


class Login(LoginView):
    """
    Login view.
    """
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
    """
    Logout view.
    """
    next_page = reverse_lazy('home')


class PasswordResetView(_PasswordResetView):
    """
    Password reset view.
    """
    success_url = reverse_lazy('accounts:password_reset_done')
    title = _('Password reset')
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    template_name = 'registration/password_reset_form.html'
    extra_email_context = {
        "expiration_time_hours": int(settings.PASSWORD_RESET_TIMEOUT / 60 / 60)
    }


class PasswordResetConfirmView(_PasswordResetConfirmView):
    """
    Password reset confirm view.
    """
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'
    title = _('Enter new password')


class PasswordResetDoneView(_PasswordResetDoneView):
    """
    Password reset done view.
    """
    template_name = 'registration/password_reset_done.html'
    title = _('Password reset sent')


class PasswordResetCompleteView(_PasswordResetCompleteView):
    """
    Password reset complete view.
    """
    template_name = 'registration/password_reset_complete.html'
    title = _('Password reset complete')


class AccountVerificationView(TemplateView):
    """
    Confirm account view.
    """
    template_name = "finance/invite_acceptance.html"

    def get(self, request, *args, **kwargs):
        """
        Handle GET request.
        """
        token = request.GET.get('t', None)

        if token is None or token == '':
            return HttpResponse("error")

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        user = get_object_or_404(User, pk=payload['user_id'])
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.verify()
        return self.render_to_response({
            "accepted": True,
        })


class LoginAsView(UserPassesTestMixin, View):
    """
    Sign in as another user.
    """

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request):
        """
        Sign in as another user.
        """
        user = get_object_or_404(User, id=request.POST.get('user'))
        login(request, user, backend='__mono.auth_backends.EmailOrUsernameModelBackend')
        return JsonResponse(
            {
                "success": True,
                "message": f"Successfully logged in as {user.username}",
            }
        )


class ConfigView(LoginRequiredMixin, TemplateView):
    """
    Show configuration page
    """

    template_name = "accounts/config.html"

    def get_context_data(self, **kwargs):
        """
        Add extra context data
        """
        context = super().get_context_data(**kwargs)

        profile: UserProfile = self.request.user.profile
        if not profile.avatar:
            profile.generate_initials_avatar()

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


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": [_("Wrong password.")]}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get("new_password") != serializer.data.get("new_password_confirmation"):
                return Response({"new_password_confirmation": [_("The two new password fields didn't match.")]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()
            login(request, request.user, backend='__mono.auth_backends.EmailOrUsernameModelBackend')
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve or update a user instance.
    """
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk, **kwargs):
        """
        Update a user instance.
        """
        if request.user.id != pk:
            return Response('You are trying to edit another user.', status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve or update a user instance.
    """

    def patch(self, request, pk, **kwargs):
        """
        Edit user profile
        """
        profile = get_object_or_404(UserProfile, pk=pk)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if request.user == profile.user:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class NotificationCountView(LoginRequiredMixin, View):
    """
    Show notification count
    """

    def get(self, *args, **kwargs):
        """
        Handle GET requests: return the number of unread notifications
        """
        qs: QuerySet[Notification] = self.request.user.notifications.filter(
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
    """
    Redirect to url in notification
    """

    model = Notification

    def get(self, *args, **kwargs):
        """
        Handle GET requests
        """
        notification: Notification = self.get_object()
        if not notification.to == self.request.user:
            raise PermissionDenied
        if not notification.read:
            notification.mark_as_read()
            messages.success(
                self.request,
                'Notification marked as read.',
            )
        if notification.action_url:
            return redirect(notification.action_url)
        return redirect('/')


class MarkNotificationsAsReadView(LoginRequiredMixin, View):
    """
    Mark notifications as read.
    """

    def post(self, request):
        """
        Mark notifications as read.
        """
        ids = json.loads(request.POST.get('ids', ''))
        if len(ids) == 0:
            raise BadRequest('No notification ids were passed.')
        notifications = Notification.objects.filter(to=request.user, read_at__isnull=True, id__in=ids)
        for notification in notifications:
            notification.mark_as_read()
        messages.success(
            request,
            f'You marked {notifications.count()} notification{"s" if notifications.count() > 1 else ""} as read.',
        )
        return JsonResponse({
            'success': True,
            'data': list(notifications.values_list('id', flat=True))
        })


class MarkNotificationsAsUnreadView(LoginRequiredMixin, View):
    """
    Mark notifications as unread.
    """

    def post(self, request):
        """
        Mark notifications as unread.
        """
        ids = json.loads(request.POST.get('ids', ''))
        if len(ids) == 0:
            raise BadRequest('No notification ids were passed.')
        notifications = Notification.objects.filter(to=request.user, read_at__isnull=False, id__in=ids)
        for notification in notifications:
            notification.mark_as_unread()
        messages.success(
            request,
            f'You marked {notifications.count()} notification{"s" if notifications.count() > 1 else ""} as unread.',
        )
        return JsonResponse({
            'success': True,
            'data': list(notifications.values_list('id', flat=True))
        })


class ApiMeView(RetrieveAPIView):
    """
    Retrive the currently logged in user.
    """

    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        return user


class ApiLogoutView(APIView):
    """
    Logout user.
    """

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
    """Show available plans."""
    template_name = "finance/plans.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        product_ids = [product.id for product in get_products()]

        context['plans'] = Plan.objects.filter(product_id__in=product_ids)
        context['free_plan'] = Plan.objects.filter(
            product_id__in=product_ids,
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
    """
    Stripe checkout view.
    """

    template_name = "finance/checkout.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'plan' not in self.request.GET:
            raise BadRequest("This endpoint needs a query parameter 'plan'.")

        plan = get_object_or_404(
            Plan,
            pk=self.request.GET.get('plan')
        )

        stripe.api_key = settings.STRIPE_SECRET_KEY
        product = stripe.Product.retrieve(plan.product_id)

        currency = 'brl' if self.request.LANGUAGE_CODE == 'pt-br' else 'usd'

        stripe_plans = stripe.Plan.list(product=product.id, active=True, currency=currency).data

        plans = []

        # Get monthly plan price
        monthly_price = list(filter(lambda price: price.interval == 'month', stripe_plans))[0]
        plans.append(monthly_price)

        # Get yearly plan price
        yearly_price = list(filter(lambda price: price.interval == 'year', stripe_plans))[0]
        plans.append(yearly_price)

        context['stripe_pk'] = settings.STRIPE_PUBLIC_KEY
        context['plan'] = plan
        context['product'] = product
        context['plans'] = plans

        return context

    def get(self, request, *args, **kwargs):
        """
        Handle redirection to the payment page
        """
        plan_id = self.request.GET.get("plan", None)
        plan = get_object_or_404(Plan, pk=plan_id)
        if plan.type != Plan.FREE:
            return self.render_to_response(self.get_context_data())
        if Subscription.objects.filter(user=request.user).exists():
            subscription: Subscription = Subscription.objects.get(user=request.user)
            success, message = subscription.cancel_at_period_end()
            messages.add_message(
                request,
                messages.SUCCESS if success else messages.ERROR,
                message
            )
        else:
            messages.error(request, "You are already subscribed to the Free Plan.")
        return redirect(to=reverse('accounts:plans'))

    def post(self, request, *args, **kwargs):
        """
        Handle form submition
        """
        payment_method_id = request.POST.get("payment_method_id")
        price_id = request.POST.get("price_id")

        stripe.api_key = settings.STRIPE_SECRET_KEY

        customer, _ = get_or_create_customer(request.user.email)
        payment_methods = get_payment_methods(customer)

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

        subscription, created = get_or_create_subscription(customer, price_id)
        msg = "You already have an active subscription." if not created else "Subscription was successfully created."
        return JsonResponse(
            {
                'success': True,
                'message': msg,
                'results': {
                    'customer': customer.id,
                    'subscription': subscription.id,
                }
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """Receive Stripe webhooks."""

    def post(self, request):
        """Receive Stripe webhooks."""
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)
        if event['type'] == 'customer.subscription.created':
            user = User.objects.get(
                email=stripe.Customer.retrieve(event.data.object.customer).email
            )
            plan: Plan = Plan.objects.get(
                product_id=stripe.Price.retrieve(event.data.object['items'].data[0].price.id).product
            )
            subscription, _ = Subscription.objects.update_or_create(
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
            subscription, _ = Subscription.objects.update_or_create(
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
            Subscription.objects.filter(user=user).delete()

        return HttpResponse(status=200)
