from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.core.mail import mail_admins
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.template.loader import get_template
from datetime import datetime
from pathlib import Path
from hashlib import sha1
import pytz
import git
import hmac
import json
import requests

def is_valid_signature(x_hub_signature, data, private_key):
    sha_name, signature  = x_hub_signature.split('=')
    if sha_name != 'sha1':
        return False
    mac = hmac.new(force_bytes(private_key), msg=force_bytes(data), digestmod=sha1)
    return hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature))

def format_datetime(datetime_string, timezone_string):
    timezone.activate(pytz.timezone(timezone_string))

    # Getting information from GitHub payload
    string_datetime = timezone.localtime(
        pytz.timezone("UTC").localize(
        datetime.strptime(
            datetime_string, 
            "%Y-%m-%dT%H:%M:%SZ"
        ), is_dst=None)
    ).strftime("%Y-%m-%d %H:%M:%S")
    return f'{string_datetime} - {timezone_string}'

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
                    timezone = "America/Sao_Paulo"

                    # Getting information from GitHub payload
                    pr_number = body['pull_request']["number"]
                    pr_title = body['pull_request']["title"]
                    pr_link = body['pull_request']["html_url"]
                    commits = body['pull_request']["commits"]
                    additions = body['pull_request']["additions"]
                    deletions = body['pull_request']["deletions"]
                    changed_files = body['pull_request']["changed_files"]
                
                    merged_at = format_datetime(
                        body['pull_request']["merged_at"], 
                        timezone
                    )

                    # Get diff
                    diff_url = body['pull_request']["diff_url"]
                    
                    merged_by = body['pull_request']["user"]['login']
                    path = Path(settings.BASE_DIR).resolve().parent
                    repo = git.Repo(path)
                    origin = repo.remotes.origin
                    fetchInfoList = origin.pull()

                    d = {
                        'title': 'Merged PR',
                        'warning_message': f'Pull Request #{pr_number}',
                        'first_line': 'Detected merged PR',
                        'main_text_lines': [
                            f'Title: {pr_title}',
                            f'Merged by: {merged_by}',
                            f'Merged at: {merged_at}',
                            f'Commits: {commits}',
                            f'Additions: {additions}',
                            f'Deletions: {deletions}',
                            f'Changed files: {changed_files}',
                        ],
                        'button_link': pr_link,
                        'button_text': f'Go to Pull Request #{pr_number}',
                        'after_button': '',
                        'unsubscribe_link': None,
                    }

                    mail_admins(
                        subject=f'Delivery Notification - PR #{pr_number}', 
                        message=get_template('email/alert.txt').render(d),
                        html_message=get_template('email/alert.html').render(d)
                    )
                    
                    print(f"Merged Pull Request detected: #{pr_number}")
                    print(fetchInfoList)
            elif event == "ping":
                return HttpResponse("pong")
            else:
                print("Invalid event.")
        else:
            print("Invalid signature.")


    return HttpResponse("ok")
