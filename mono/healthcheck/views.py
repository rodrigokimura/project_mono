from django.conf import settings
from django.http import JsonResponse
from pathlib import Path
import git
import os
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt


def is_valid_signature(x_hub_signature, data, private_key):
    # x_hub_signature and data are from the webhook payload
    # private key is your webhook secret
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

def healthcheck(request):
    return JsonResponse({'version': settings.APP_VERSION})

@csrf_exempt
def update_app(request):
    if request.method == "POST":
        x_hub_signature = request.headers.get('X-Hub-Signature')
        w_secret = settings.GITHUB_SECRET
        if is_valid_signature(x_hub_signature, request.body, w_secret):
            event = request.headers.get('X-GitHub-Event')
            if event == "push":
                path = Path(settings.BASE_DIR).resolve().parent
                repo = git.Repo(path)
                origin = repo.remotes.origin
                origin.pull()
                print("Successfully updated repo!")
            elif event == "ping":
                return JsonResponse({'msg': "pong"})
            else:
                print("Invalid event.")
        else:
            print("Invalid signature.")


    return JsonResponse({'status': "ok"})
