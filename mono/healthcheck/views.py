from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.encoding import force_bytes
from datetime import datetime
from hashlib import sha1
import pytz
import hmac
import json
from .models import PullRequest

def is_valid_signature(x_hub_signature, data, private_key):
    sha_name, signature  = x_hub_signature.split('=')
    if sha_name != 'sha1':
        return False
    mac = hmac.new(force_bytes(private_key), msg=force_bytes(data), digestmod=sha1)
    return hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature))

def string_to_localized_datetime(datetime_string):
    return pytz.timezone("UTC").localize(
        datetime.strptime(
            datetime_string, 
            "%Y-%m-%dT%H:%M:%SZ"
        ), is_dst=None)
    

def healthcheck(request):
    return JsonResponse({'version': settings.APP_VERSION})

@csrf_exempt
def update_app(request):
    if request.method == "POST":
        x_hub_signature = request.headers.get('X-Hub-Signature')
        w_secret = settings.GITHUB_SECRET
        
        body = json.loads(request.body.decode('utf-8'))
        if is_valid_signature(x_hub_signature, request.body, w_secret):
            event = request.headers.get('X-GitHub-Event')
            if event == "pull_request":
                ref = body['pull_request']['base']['ref']
                if body["action"] == "closed" and body["pull_request"]["merged"] and ref == 'master':

                    pull_request, created = PullRequest.objects.update_or_create(
                        number = body['pull_request']["number"],
                        author = body['pull_request']["user"]['login'],
                        commits = body['pull_request']["commits"],
                        additions = body['pull_request']["additions"],
                        deletions = body['pull_request']["deletions"],
                        changed_files = body['pull_request']["changed_files"],
                        merged_at = string_to_localized_datetime(body['pull_request']["merged_at"])
                    )

                    link = body['pull_request']["html_url"]

                    pull_request.pull(link=link)

            elif event == "ping":
                print("Ping sent from GitHub.")
                return HttpResponse("pong")
            else:
                print("Invalid event.")
        else:
            print("Invalid signature.")

    return HttpResponse("ok")
