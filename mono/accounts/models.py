from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=256, blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=(
            ('', 'Gender'),
            ('m', 'Male'),
            ('f', 'Female'),
            ('n', 'I prefer not to say')),
        blank=False,
        null=False)

    avatar = models.ImageField(upload_to=user_directory_path, null=True)

    def __str__(self):
        return str(self.user)
