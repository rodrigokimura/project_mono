from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def card_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


# Create your models here.
class BaseModel(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Project(BaseModel):
    deadline = models.DateTimeField()
    # milestones =
    assigned_to = models.ManyToManyField(User, related_name="assigned_projects")


class Board(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(User, related_name="assigned_boards")


class Bucket(BaseModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    order = models.IntegerField()


class Card(BaseModel):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    order = models.IntegerField()
    assigned_to = models.ManyToManyField(User, related_name="assigned_cards")
    description = models.TextField(max_length=255)
    files = models.FileField(upload_to=None, max_length=100)
    completed_at = models.DateTimeField()
    completed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="completed_cards")
    # progress


class Item(BaseModel):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    checked_at = models.DateTimeField()
    checked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checked_items")
