from django.contrib.auth import get_user_model
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User, Group
from . import models
from django import forms
from django.forms import ValidationError
from django.db.models.signals import post_save
# from PIL import get

class UserCreateForm(auth_forms.UserCreationForm):
    error_css_class = 'error'

    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Display name"
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields["email"].label = "Email address"
        self.fields['email'].widget.attrs.update({'placeholder': 'Email address'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
    
    def clean(self):
       email = self.cleaned_data.get('email')
       if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
       return self.cleaned_data
    
    def add_user_to_public_group(sender, instance, created, **kwargs):
        """Post-create user signal that adds the user to everyone group."""
        try:
            if created:
                instance.groups.add(Group.objects.get(name='Cliente'))
        except Group.DoesNotExist:
            pass
          

    post_save.connect(add_user_to_public_group, sender=User)

class UserProfileForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update({'placeholder': 'Phone'})
        self.fields['gender'].widget.attrs.update({'class': 'ui dropdown'})
        self.fields['avatar'].widget.attrs.update({'placeholder': 'Avatar'})


    class Meta:
        model = models.UserProfile
        fields = (
            "phone", 
            "gender",
            "avatar"
        )

    # def clean_avatar(self):
    #     avatar = self.cleaned_data['avatar']

    #     try:
    #         w, h = get_image_dimensions(avatar)

    #         #validate dimensions
    #         max_width = max_height = 100
    #         if w > max_width or h > max_height:
    #             raise forms.ValidationError(
    #                 u'Please use an image that is '
    #                  '%s x %s pixels or smaller.' % (max_width, max_height))

    #         #validate content type
    #         main, sub = avatar.content_type.split('/')
    #         if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
    #             raise forms.ValidationError(u'Please use a JPEG, '
    #                 'GIF or PNG image.')

    #         #validate file size
    #         if len(avatar) > (20 * 1024):
    #             raise forms.ValidationError(
    #                 u'Avatar file size may not exceed 20k.')

    #     except AttributeError:
    #         """
    #         Handles case when we are updating the user profile
    #         and do not supply a new avatar
    #         """
    #         pass

    #     return avatar




class CustomPasswordResetForm(auth_forms.PasswordResetForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def send_mail(self, *args, **kwargs):
        
        args = list(args)
        if args[3] == None:
            args[3] = "naoresponda@voitkemp.com"
        args = tuple(args)

        super().send_mail(*args, **kwargs)
