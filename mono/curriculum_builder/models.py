"""Curriculum Builder's models"""
from django.contrib.auth import get_user_model
from django.db import models

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
    address = models.CharField(max_length=200)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_picture = models.ImageField(null=True, blank=True)
    bio = models.TextField(max_length=1000)
    social_media_profiles = models.ManyToManyField('SocialMediaProfile')
    skills = models.ManyToManyField('Skill')
    work_experiences = models.ManyToManyField('WorkExperience')


class SocialMediaProfile(BaseModel):
    """Hold links to social media profiles"""

    class Platform(models.TextChoices):
        """Platform choices"""
        LINKEDIN = 'LI', 'LinkedIn'
        GITHUB = 'GH', 'Github'
        TWITTER = 'TT', 'Twitter'
        FACEBOOK = 'FB', 'Facebook'
        INSTAGRAM = 'IG', 'Instagram'
        WHATSAPP = 'WA', 'WhatsApp'


    platform = models.CharField(max_length=10, choices=Platform.choices)
    link = models.URLField()


class Skill(BaseModel):
    """Skills as part of a Curriculum"""
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    image = models.ImageField()


class WorkExperience(BaseModel):
    """Work experiences as part of a Curriculum"""
    started_at = models.DateField()
    ended_at = models.DateField(null=True, blank=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    description = models.TextField(max_length=1000)


class Company(BaseModel):
    """Company in which user has worked"""
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    image = models.ImageField()


class Acomplishment(BaseModel, OrderedModel):
    """Acomplishments realized within a work experience"""
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    work_experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE)
    order_with_respect_to = 'work_experiene'
