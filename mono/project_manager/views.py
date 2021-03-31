from django.shortcuts import render
from django.views.generic import ListView
from django.utils import timezone

from . import models

# Create your views here.


def index(request):
    my_dict = {
        "insert_content": "inserindo conteúdo da views",
        'access_records': "teste"
    }
    return render(request=request, template_name='homepage/home.html', context=my_dict)


class ProjectListView(ListView):
    model = models.Project
    paginate_by = 100  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
