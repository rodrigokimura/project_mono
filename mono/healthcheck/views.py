import hmac
import json
import logging
from datetime import datetime, timedelta
from hashlib import sha1

import pytz
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Sum
from django.db.models.expressions import Value
from django.db.models.fields import IntegerField
from django.db.models.functions.comparison import Coalesce
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
        if not is_valid_signature(x_hub_signature, request.body):
            logging.info("Invalid signature.")
            return HttpResponse(status=403)
        
        event = request.headers.get('X-GitHub-Event')
        if event == 'ping':
            logging.info("Ping sent from GitHub.")
            return HttpResponse("pong")

        if event != "pull_request":
            logging.info("Invalid event.")
            return HttpResponse(status=403)

        body = json.loads(request.body.decode('utf-8'))
        ref = body['pull_request']['base']['ref']
        if body["action"] == "closed" and body["pull_request"]["merged"] and ref == 'master':
            pull_request = body['pull_request']
            PullRequest.objects.update_or_create(
                number=pull_request["number"],
                defaults={
                    'author': pull_request["user"]['login'],
                    'last_commit_sha': pull_request['base']['sha'],
                    'commits': pull_request["commits"],
                    'additions': pull_request["additions"],
                    'deletions': pull_request["deletions"],
                    'changed_files': pull_request["changed_files"],
                    'merged_at': string_to_localized_datetime(pull_request["merged_at"])
                }
            )
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

        d = datetime.today() - timedelta(weeks=52)
        initial_date = datetime.fromisocalendar(
            year=d.isocalendar()[0],
            week=d.isocalendar()[1],
            day=1,
        ) - timedelta(days=1)
        days = (datetime.today() - initial_date).days

        data_0 = []
        data_1 = []
        data_2 = []
        data_3 = []
        data_4 = []
        data_5 = []
        data_6 = []
        for i in range(days + 1):
            date = initial_date + timedelta(days=i)
            data = pull_requests.filter(
                merged_at__date=date
            ).aggregate(
                sum=Coalesce(
                    Sum('commits'),
                    Value(0),
                    output_field=IntegerField()
                )
            )['sum']
            if i % 7 == 0:
                data_0.append({'d': date, 'c': data})
            elif i % 7 == 1:
                data_1.append({'d': date, 'c': data})
            elif i % 7 == 2:
                data_2.append({'d': date, 'c': data})
            elif i % 7 == 3:
                data_3.append({'d': date, 'c': data})
            elif i % 7 == 4:
                data_4.append({'d': date, 'c': data})
            elif i % 7 == 5:
                data_5.append({'d': date, 'c': data})
            elif i % 7 == 6:
                data_6.append({'d': date, 'c': data})
        context['data_0'] = data_0
        context['data_1'] = data_1
        context['data_2'] = data_2
        context['data_3'] = data_3
        context['data_4'] = data_4
        context['data_5'] = data_5
        context['data_6'] = data_6
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
