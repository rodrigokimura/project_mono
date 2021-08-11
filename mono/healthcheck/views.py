from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from datetime import datetime
from hashlib import sha1
import pytz
import hmac
import json
import git
import difflib
from .models import PullRequest


def is_valid_signature(x_hub_signature, data, private_key):
    sha_name, signature = x_hub_signature.split('=')
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
    current_pull_request = PullRequest.objects.exclude(deployed_at=None).latest('number')
    return JsonResponse(
        {
            'build_number': current_pull_request.build_number
        }
    )


@csrf_exempt
def update_app(request):
    """
    This view receives a POST notification from a GitHub webhook
    everytime a Pull Request is successfully merged.
    """
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
                        number=body['pull_request']["number"],
                        defaults={
                            'author': body['pull_request']["user"]['login'],
                            'commits': body['pull_request']["commits"],
                            'additions': body['pull_request']["additions"],
                            'deletions': body['pull_request']["deletions"],
                            'changed_files': body['pull_request']["changed_files"],
                            'merged_at': string_to_localized_datetime(body['pull_request']["merged_at"])
                        }
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


class Deploy(UserPassesTestMixin, TemplateView):
    template_name = 'healthcheck/deploy.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        def _get_diff_context(diff_index):
            for i, d in enumerate(diff_index):
                if d.change_type in ['M']:
                    try:
                        a = d.a_blob.data_stream.read().decode("utf-8").split("\n")
                        b = d.b_blob.data_stream.read().decode("utf-8").split("\n")
                        human_diff = []
                        for line in difflib.context_diff(a, b):
                            human_diff.append(line)
                        yield (i, d.change_type, d.a_path, human_diff)
                    except Exception as e:
                        print(repr(e))
                        yield (i, d.change_type, d.a_path, None)

                else:
                    try:
                        if d.a_blob is not None:
                            file = d.a_blob.data_stream.read().decode("utf-8").split("\n")
                        elif d.b_blob is not None:
                            file = d.b_blob.data_stream.read().decode("utf-8").split("\n")
                        yield (i, d.change_type, d.a_path, file)
                    except Exception as e:
                        print(repr(e))
                        yield (i, d.change_type, d.a_path, None)

        context = super().get_context_data(**kwargs)
        context['last_pr'] = PullRequest.objects.latest('number')

        path = Path(settings.BASE_DIR).resolve().parent
        repo = git.Repo(path)
        local_master = repo.commit("master")
        remote_master = repo.commit("origin/master")
        # diff_index = remote_master.diff(local_master)
        diff_index = local_master.diff(remote_master)
        context['diff_items'] = _get_diff_context(diff_index)
        return context

    def post(self, request):
        pr = get_object_or_404(PullRequest, pk=request.POST.get('pk', None))
        pr.deploy()
        return JsonResponse(
            {
                'success': True,
                'message': 'Deployed successfully.',
                'data': {
                    'number': pr.number,
                    'build_number': pr.build_number,
                    'deployed_at': pr.deployed_at,
                },
            }
        )
