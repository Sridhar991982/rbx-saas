from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from forms import HomeSignupForm


def home_or_dashboard(request):
    return home(request)


def home(request):
    return render(request, 'home.html', {
        'signup_form': HomeSignupForm,
    })


@login_required
def dashboard(request):
    return home(request)


def signup(request, from_home=False):
    return render(request, 'signup.html')


def profile(request, username):
    return home(request)
