from django.conf import settings
from django.http import JsonResponse
from pathlib import Path
import git
import os
import hmac
import hashlib
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes
from hashlib import sha1
from django.core.mail import mail_admins




def is_valid_signature(x_hub_signature, data, private_key):
    sha_name, signature  = x_hub_signature.split('=')
    if sha_name != 'sha1':
        return False
    mac = hmac.new(force_bytes(private_key), msg=force_bytes(data), digestmod=sha1)
    return hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature))

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
                    pr_number = body['pull_request']["number"]
                    merged_at = body['pull_request']["merged_at"]
                    merged_by = body['pull_request']["user"]['login']
                    path = Path(settings.BASE_DIR).resolve().parent
                    repo = git.Repo(path)
                    origin = repo.remotes.origin
                    fetchInfoList = origin.pull()
                    mail_admins(
                        f'[MONO PROJECT] Delivery Notification - PR #{pr_number}', 
                        f'Merged PR #{pr_number} triggered this code delivery. Merged at {merged_at} by {merged_by}')
                    print(f"Merged Pull Request detected: #{pr_number}")
                    print(fetchInfoList)
            elif event == "ping":
                return JsonResponse({'msg': "pong"})
            else:
                print("Invalid event.")
        else:
            print("Invalid signature.")


    return JsonResponse({'status': "ok"})
