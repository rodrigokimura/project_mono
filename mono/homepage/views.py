from django.shortcuts import render
from django.contrib.auth import views

# Create your views here.


class Login(views.LoginView):
    template_name = "homepage/home.html"


def index(request):
    my_dict = {
        "insert_content": "inserindo conteúdo da views",
        'access_records': "teste"
    }
    return render(request=request, template_name='homepage/home.html', context=my_dict)
