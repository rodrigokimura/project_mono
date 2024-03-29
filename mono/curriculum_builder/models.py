"""Curriculum Builder's models"""
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Max, Min
from ordered_model.models import OrderedModel

User = get_user_model()


class BaseModel(models.Model):
    """Abstract model for this app"""

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Curriculum(BaseModel):
    """Curriculum created by user"""

    class Style(models.TextChoices):
        """
        Page style choices.
        Each option must map to a template /curriculum_builder/styles/{value}.html
        """

        SEMANTIC = "semantic", "Semantic"
        TYPEWRITER = "typewriter", "Typewriter"

    address = models.CharField(max_length=200)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_picture = models.ImageField(null=True, blank=True)
    bio = models.TextField(max_length=1000)
    style = models.CharField(
        choices=Style.choices, default=Style.SEMANTIC.value, max_length=50
    )

    class Meta:
        verbose_name = "curriculum"
        verbose_name_plural = "curricula"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class SocialMediaProfile(BaseModel):
    """Hold links to social media profiles"""

    class Platform(models.TextChoices):
        """Platform choices"""

        LINKEDIN = "LI", "LinkedIn"
        GITHUB = "GH", "Github"
        TWITTER = "TT", "Twitter"
        FACEBOOK = "FB", "Facebook"
        INSTAGRAM = "IG", "Instagram"
        WHATSAPP = "WA", "WhatsApp"

    platform = models.CharField(max_length=10, choices=Platform.choices)
    link = models.URLField()
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="social_media_profiles",
    )

    def __str__(self) -> str:
        return f"{self.platform}: {self.link}"


class Skill(BaseModel):
    """Skills as part of a Curriculum"""

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    image = models.ImageField(null=True, blank=True)
    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, related_name="skills"
    )

    def __str__(self) -> str:
        return self.name


class WorkExperience(BaseModel):
    """Work experiences as part of a Curriculum"""

    started_at = models.DateField()
    ended_at = models.DateField(null=True, blank=True)
    company = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="work_experiences"
    )
    job_title = models.TextField(max_length=50)
    description = models.TextField(max_length=1000)

    def __str__(self) -> str:
        return f"{self.job_title} at {self.company}, {self.started_at} to {self.ended_at}"


class Company(BaseModel):
    """Company in which user has worked"""

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    image = models.ImageField(null=True, blank=True)
    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, related_name="companies"
    )

    class Meta:
        verbose_name = "company"
        verbose_name_plural = "companies"

    def __str__(self) -> str:
        return self.name

    @property
    def started_at(self):
        return WorkExperience.objects.filter(
            company=self,
        ).aggregate(
            Min("started_at")
        )["started_at__min"]

    @property
    def ended_at(self):
        """End date of the last work experience"""
        qs = WorkExperience.objects.filter(
            company=self,
        )
        if qs.filter(ended_at__isnull=True).exists():
            return None
        return qs.aggregate(Max("ended_at"))["ended_at__max"]


class Acomplishment(BaseModel, OrderedModel):
    """Acomplishments realized within a work experience"""

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    work_experience = models.ForeignKey(
        WorkExperience, on_delete=models.CASCADE, related_name="acomplishments"
    )

    order_with_respect_to = "work_experience"

    class Meta:
        ordering = ("work_experience", "order")

    def __str__(self) -> str:
        return self.title
