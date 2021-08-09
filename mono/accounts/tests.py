from django.test import TestCase
from .models import User
from .forms import UserCreateForm, UserProfileForm


class UserCreateFormTest(TestCase):

    fixtures = ["icon.json"]

    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            email='test@test.com'
        )

    def test_username_field_label(self):
        form = UserCreateForm()
        self.assertTrue(form.fields['username'].label is None or form.fields['username'].label == 'Display name')

    def test_email_field_label(self):
        form = UserCreateForm()
        self.assertTrue(form.fields['email'].label is None or form.fields['email'].label == 'Email address')

    def test_form_clean(self):
        data = {
            'username': 'testclient',
            'email': 'test@test.com',
            'password1': 'qweasd@123',
            'password2': 'qweasd@123',
        }
        form = UserCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'][0], 'Email exists')
        data = {
            'username': 'username',
            'email': 'randomemail@test.com',
            'password1': 'test@123',
            'password2': 'test@123',
        }
        form = UserCreateForm(data)
        self.assertTrue(form.is_valid())


class UserProfileFormTest(TestCase):

    def test_username_field_label(self):
        form = UserProfileForm()
        self.assertTrue(form.fields['avatar'].label is None or form.fields['avatar'].label == 'Avatar')
