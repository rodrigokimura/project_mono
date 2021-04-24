from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def environment(request):
    return {'APP_ENV': settings.APP_ENV}


def language_extras(request):
    tinyMCE_languages = {
        'pt-br': 'pt_BR'
    }
    tinyMCE_language = tinyMCE_languages.get(request.LANGUAGE_CODE)
    return {
        'LANGUAGE_EXTRAS': settings.LANGUAGE_EXTRAS,
        'tinyMCE_language': tinyMCE_language
    }


def users(request):
    return {
        'users': User.objects.filter(is_active=True).exclude(id=request.user.id)
    }


def analytical_app(request):
    return {'CLICKY_SITE_ID': settings.CLICKY_SITE_ID}
