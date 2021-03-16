from django.conf import settings
from django.http import JsonResponse
from pathlib import Path
import git
import os
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes
from hashlib import sha1




def is_valid_signature(x_hub_signature, data, private_key):
    # x_hub_signature and data are from the webhook payload
    # private key is your webhook secret
    sha_name, signature  = x_hub_signature.split('=')
    if sha_name != 'sha1':
        return False
    mac = hmac.new(force_bytes(private_key), msg=force_bytes(data), digestmod=sha1)
    max_hex = mac.hexdigest()

    return hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature))

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
                fetchInfoList = origin.pull()
                print("Successfully updated repo!")
                print(fetchInfoList)
            elif event == "ping":
                return JsonResponse({'msg': "pong"})
            else:
                print("Invalid event.")
        else:
            print("Invalid signature.")


    return JsonResponse({'status': "ok"})
