from django.db import models
User = get_user_model()


# Create your models here.
class Object(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    created_by = models.ForeignKey(User, verbose_name="Created By", on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="Crated At", auto_now_add=True)
    active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return self.name