from django.shortcuts import render
from forms import HomeSignupForm


def home_or_dashboard(request):
    return home(request)


def home(request):
    return render(request, 'home.html', {
        'signup_form': HomeSignupForm,
    })


def dashboard(request):
    return home(request)
