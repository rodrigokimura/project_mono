"""Useful context processors"""
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def environment(request):
    return {'APP_ENV': settings.APP_ENV}


def language_extras(request):
    """Extra language settings for the template context"""
    tinymce_languages = {
        'pt-br': 'pt_BR'
    }
    tinymce_language = tinymce_languages.get(request.LANGUAGE_CODE)
    return {
        'LANGUAGE_EXTRAS': settings.LANGUAGE_EXTRAS,
        'tinymce_language': tinymce_language
    }
