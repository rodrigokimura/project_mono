from django.conf import settings
from django.http import JsonResponse

def healthcheck(self):
    return JsonResponse({'version': settings.APP_VERSION})