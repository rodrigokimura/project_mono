from django.conf import settings

def environment(request):
    return {'APP_ENV': settings.APP_ENV}