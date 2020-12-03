from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.messages import get_messages
from django.contrib.messages import constants as message


@csrf_exempt
def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))


@csrf_exempt
def login(request):
    if request.POST.get("username", "") == "pxUser":
        if request.POST.get("password", "") == "1234":
            return redirect('/profile')
        else:
            return redirect('/')
    else:
        return redirect('/')


@csrf_exempt
def profile(request):
    template = loader.get_template('profile.html')
    context = {}
    return HttpResponse(template.render(context, request))


@csrf_exempt
def fp(request):
    template = loader.get_template('fp.html')
    context = {}
    return HttpResponse(template.render(context, request))
