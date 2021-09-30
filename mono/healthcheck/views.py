import hmac
import json
import logging
from datetime import datetime
from hashlib import sha1

import pytz
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from .models import PullRequest
from .tasks import deploy_app


def is_valid_signature(x_hub_signature, data):
    private_key = settings.GITHUB_SECRET
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
    current_pr: PullRequest = PullRequest.objects.exclude(deployed_at=None).latest('number')
    return JsonResponse({'build_number': current_pr.build_number})


@csrf_exempt
def github_webhook(request):
    """
    This view receives a POST notification from a GitHub webhook
    everytime a Pull Request is successfully merged.
    """
    if request.method == "POST":
        x_hub_signature = request.headers.get('X-Hub-Signature')
        if is_valid_signature(x_hub_signature, request.body):
            body = json.loads(request.body.decode('utf-8'))
            event = request.headers.get('X-GitHub-Event')
            if event == "pull_request":
                ref = body['pull_request']['base']['ref']
                if body["action"] == "closed" and body["pull_request"]["merged"] and ref == 'master':
                    pull_request = body['pull_request']
                    pr, created = PullRequest.objects.update_or_create(
                        number=pull_request["number"],
                        defaults={
                            'author': pull_request["user"]['login'],
                            'commits': pull_request["commits"],
                            'additions': pull_request["additions"],
                            'deletions': pull_request["deletions"],
                            'changed_files': pull_request["changed_files"],
                            'merged_at': string_to_localized_datetime(pull_request["merged_at"])
                        }
                    )
            elif event == "ping":
                logging.info("Ping sent from GitHub.")
                return HttpResponse("pong")
            else:
                logging.info("Invalid event.")
        else:
            logging.info("Invalid signature.")
    return HttpResponse("ok")


class Deploy(UserPassesTestMixin, TemplateView):
    template_name = 'healthcheck/deploy.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_pr'] = PullRequest.objects.latest('number')
        pull_requests = PullRequest.objects.all()
        context['pull_requests'] = pull_requests
        return context

    # def get_context_data(self, **kwargs):
    #     def _get_diff_context(diff_index):
    #         for i, d in enumerate(diff_index):
    #             if d.change_type in ['M']:
    #                 try:
    #                     a = d.a_blob.data_stream.read().decode("utf-8").split("\n")
    #                     b = d.b_blob.data_stream.read().decode("utf-8").split("\n")
    #                     human_diff = []
    #                     for line in difflib.context_diff(a, b):
    #                         human_diff.append(line)
    #                     yield (i, d.change_type, d.a_path, human_diff)
    #                 except Exception:
    #                     yield (i, d.change_type, d.a_path, None)
    #             else:
    #                 try:
    #                     if d.a_blob is not None:
    #                         file = d.a_blob.data_stream.read().decode("utf-8").split("\n")
    #                     elif d.b_blob is not None:
    #                         file = d.b_blob.data_stream.read().decode("utf-8").split("\n")
    #                     yield (i, d.change_type, d.a_path, file)
    #                 except Exception:
    #                     yield (i, d.change_type, d.a_path, None)
    #     context = super().get_context_data(**kwargs)
    #     path = Path(settings.BASE_DIR).resolve().parent
    #     repo = git.Repo(path)
    #     local_master = repo.commit("master")
    #     remote_master = repo.commit("origin/master")
    #     diff_index = local_master.diff(remote_master)
    #     context['diff_items'] = _get_diff_context(diff_index)
    #     return context

    def post(self, request):
        pr = get_object_or_404(PullRequest, pk=request.POST.get('pk', None))
        deploy_app(pr.number)
        return JsonResponse(
            {
                'success': True,
                'message': 'Successfully scheduled deployment.',
                'data': {
                    'number': pr.number,
                },
            }
        )
