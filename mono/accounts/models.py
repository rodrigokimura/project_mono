import random
from datetime import timedelta
from xml.sax.saxutils import escape as xml_escape

import jwt
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
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Notification(models.Model):
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

    def __str__(self) -> str:
        return self.title

    @property
    def read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = timezone.now()
        self.save()


class UserProfile(models.Model):
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
        self.verified_at = timezone.now()
        self.save()
        Notification.objects.create(
            title="Account verification",
            message="Your account was successfully verified.",
            icon='exclamation',
            to=self.user
        )

    def send_verification_email(self):

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

        d = {
            'warning_message': 'Account verification',
            'first_line': 'We need to verify your account. Please click the button below.',
            'button_text': 'Verify',
            'button_link': full_link,
        }

        msg = EmailMultiAlternatives(
            subject='Invite',
            body=text.render(d),
            from_email=settings.EMAIL_HOST_USER,
            to=[self.user.email])
        msg.attach_alternative(html.render(d), "text/html")
        msg.send(fail_silently=False)

        Notification.objects.create(
            title="Account verification",
            message="We've sent you an email to verify your account.",
            icon='exclamation',
            to=self.user,
        )

    def generate_initials_avatar(self):
        COLORS = [
            ['#DF7FD7', '#DF7FD7', '#591854'],
            ['#E3CAC8', '#DF8A82', '#5E3A37'],
            ['#E6845E', '#E05118', '#61230B'],
            ['#E0B050', '#E6CB97', '#614C23'],
            ['#9878AD', '#492661', '#C59BE0'],
            ['#787BAD', '#141961', '#9B9FE0'],
            ['#78A2AD', '#104F61', '#9BD1E0'],
            ['#78AD8A', '#0A6129', '#9BE0B3'],
        ]
        INITIALS_SVG_TEMPLATE = """
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
        random_color = random.choice(COLORS)
        svg_avatar = INITIALS_SVG_TEMPLATE.format(**{
            'color1': random_color[0],
            'color2': random_color[1],
            'text_color': random_color[2],
            'text': xml_escape(initials.upper()),
        }).replace('\n', '')
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(svg_avatar.encode('UTF-8'))
        img_temp.flush()
        self.avatar.save(
            "initials.svg",
            File(img_temp),
            save=True,
        )
