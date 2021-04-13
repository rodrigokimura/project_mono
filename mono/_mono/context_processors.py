from django.conf import settings


def environment(request):
    return {'APP_ENV': settings.APP_ENV}


def language_extras(request):
    return {'LANGUAGE_EXTRAS': settings.LANGUAGE_EXTRAS}


def analytical_app(request):
    return {'CLICKY_SITE_ID': settings.CLICKY_SITE_ID}
