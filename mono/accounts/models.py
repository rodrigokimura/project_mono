"""Finance's models"""
import random
from datetime import datetime, timedelta
from typing import Tuple
from xml.sax.saxutils import escape as xml_escape

import jwt
import pytz
import stripe
from __mono.decorators import stripe_exception_handler
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.fields import DateTimeField
from django.template.loader import get_template
from django.urls.base import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def user_directory_path(instance, filename):
    """file will be uploaded to MEDIA_ROOT/user_<id>/<filename>"""
    return f'user_{instance.user.id}/{filename}'


class Notification(models.Model):
    """Notification model"""
    title = models.CharField(max_length=50)
    message = models.CharField(max_length=255)
    to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=50, default='bell')
    read_at = models.DateTimeField(blank=True, null=True, default=None)
    action_url = models.CharField(max_length=1000, blank=True, null=True, default=None)

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ['created_at']

    def __str__(self) -> str:
        return self.title

    @property
    def read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = timezone.now()
        self.save()

    def mark_as_unread(self):
        self.read_at = None
        self.save()


class UserProfile(models.Model):
    """User profile stores extra information about the user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True,
        default=None,
    )
    verified_at = DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.user)

    def verify(self):
        """Activate the user's account"""
        self.verified_at = timezone.now()
        self.save()
        Notification.objects.create(
            title="Account verification",
            message="Your account was successfully verified.",
            icon='exclamation',
            to=self.user
        )

    def send_verification_email(self):
        """Send an email to the user to verify their account"""

        token = jwt.encode(
            {
                "exp": timezone.now() + timedelta(days=30),
                "user_id": self.user.id
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        template_html = 'email/alert.html'
        template_text = 'email/alert.txt'

        text = get_template(template_text)
        html = get_template(template_html)

        site = settings.SITE

        full_link = site + f"{reverse('accounts:verify')}?t={token}"

        context = {
            'warning_message': 'Account verification',
            'first_line': 'We need to verify your account. Please click the button below.',
            'button_text': 'Verify',
            'button_link': full_link,
        }

        msg = EmailMultiAlternatives(
            subject='Invite',
            body=text.render(context),
            from_email=settings.EMAIL_HOST_USER,
            to=[self.user.email])
        msg.attach_alternative(html.render(context), "text/html")
        msg.send(fail_silently=False)

        Notification.objects.create(
            title="Account verification",
            message="We've sent you an email to verify your account.",
            icon='exclamation',
            to=self.user,
        )

    def generate_initials_avatar(self):
        """Generate an avatar in SVG format from the user's initials"""
        colors = [
            ['#DF7FD7', '#DF7FD7', '#591854'],
            ['#E3CAC8', '#DF8A82', '#5E3A37'],
            ['#E6845E', '#E05118', '#61230B'],
            ['#E0B050', '#E6CB97', '#614C23'],
            ['#9878AD', '#492661', '#C59BE0'],
            ['#787BAD', '#141961', '#9B9FE0'],
            ['#78A2AD', '#104F61', '#9BD1E0'],
            ['#78AD8A', '#0A6129', '#9BE0B3'],
        ]
        initials_svg_template = """
            <svg xmlns="http://www.w3.org/2000/svg"
                    pointer-events="none"
                    width="200" height="200">
                <defs>
                    <linearGradient id="grad">
                    <stop offset="0%" stop-color="{color1}" />
                    <stop offset="100%" stop-color="{color2}" />
                    </linearGradient>
                </defs>
                <rect width="200" height="200" rx="0" ry="0" fill="url(#grad)"></rect>
                <text text-anchor="middle" y="50%" x="50%" dy="0.35em"
                    pointer-events="auto" fill="{text_color}" font-family="sans-serif"
                    style="font-weight: 400; font-size: 80px">{text}</text>
            </svg>
        """.strip()
        initials = self.user.username[0]
        random_color = random.choice(colors)
        svg_avatar = initials_svg_template.format(**{
            'color1': random_color[0],
            'color2': random_color[1],
            'text_color': random_color[2],
            'text': xml_escape(initials.upper()),
        }).replace('\n', '')
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(svg_avatar.encode('UTF-8'))
        img_temp.flush()
        try:
            self.avatar.save(
                "initials.svg",
                File(img_temp),
                save=True,
            )
        except OSError:
            pass


class Plan(models.Model):
    """
    Stores data about the plans user can subscribve to.
    This models has data used to populate the checkout page.
    Those are related to Stripe products."""

    FREE = 'FR'
    LIFETIME = 'LT'
    DEFAULT = 'DF'
    RECOMMENDED = 'RC'

    TYPE_CHOICES = [
        (FREE, _('Free')),
        (LIFETIME, _('Lifetime')),
        (DEFAULT, _('Default')),
        (RECOMMENDED, _('Recommended')),
    ]

    product_id = models.CharField(max_length=100, help_text="Stores the stripe unique identifiers")
    name = models.CharField(max_length=100, help_text="Display name used on the template")
    description = models.TextField(max_length=500, help_text="Description text used on the template")
    icon = models.CharField(max_length=50, help_text="Icon rendered in the template")
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        help_text="Used to customize the template based on this field."
        "For instance, the basic plan will be muted and the recommended one is highlighted."
    )
    order = models.IntegerField(unique=True, help_text="Used to sort plans on the template.")

    class Meta:
        verbose_name = _("plan")
        verbose_name_plural = _("plans")
        ordering = ["order"]

    def __str__(self) -> str:
        return self.name


class Feature(models.Model):
    """
    Stores features related to the plans user can subscribe to.
    This models is used to populate the checkout page.
    Those are related to plans that are related to Stripe products."""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    icon = models.CharField(max_length=50, help_text="Icon rendered in the template")
    short_description = models.CharField(max_length=30)
    full_description = models.TextField(max_length=200)
    internal_description = models.TextField(
        max_length=1000,
        null=True,
        blank=True,
        default=None,
        help_text="This is used by staff and is not displayed to user in the template."
    )
    display = models.BooleanField(help_text="Controls wether feature is shown on the template", default=True)

    class Meta:
        verbose_name = _("feature")
        verbose_name_plural = _("features")

    def __str__(self) -> str:
        return f"{self.plan.name} - {self.short_description}"


class Subscription(models.Model):
    """
    Stores subscriptions made by users. This is used to provide plan features and limitations to user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancel_at = models.DateTimeField(null=True, blank=True)
    event_id = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    @property
    def status(self):
        """Get subcription status"""
        if self.cancel_at is None:
            status = "active"
        elif self.cancel_at > timezone.now():
            status = "pending"
        elif self.cancel_at <= timezone.now():
            status = "error"
        return status

    @stripe_exception_handler
    def cancel_at_period_end(self) -> Tuple[bool, str]:
        """Set the subscription to cancel at period end"""
        # Update Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = stripe.Customer.list(email=self.user.email).data[0]
        subscription = stripe.Subscription.list(customer=customer.id).data[0]
        subscription = stripe.Subscription.modify(subscription.id, cancel_at_period_end=True)

        # Update model
        self.cancel_at = timezone.make_aware(
            datetime.fromtimestamp(subscription.cancel_at),
            pytz.timezone(settings.STRIPE_TIMEZONE)
        )
        self.save()
        return (True, "Your subscription has been scheduled to be cancelled at the end of your renewal date.")

    def abort_cancellation(self):
        """Abort the cancellation of the Stripe subscription."""
        if self.cancel_at is not None:
            # Update Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.list(email=self.user.email).data[0]
            subscription = stripe.Subscription.list(customer=customer.id).data[0]
            subscription = stripe.Subscription.modify(subscription.id, cancel_at_period_end=False)

            # Update model
            self.cancel_at = None
            self.save()

    # def cancel_now(self):
    #     self.cancel_at = None
    #     self.plan = Plan.objects.get(type=Plan.FREE)
    #     self.save()
