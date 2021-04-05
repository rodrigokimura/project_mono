from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.fields import DateTimeField
from django.utils import timezone

User = get_user_model()


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
