from django.shortcuts import render

# Create your views here.
def index(request):
    my_dict = {
        "insert_content":"inserindo conteúdo da views",
        'access_records':"teste"
    }
    return render(request=request, template_name='homepage/home.html',context=my_dict)

