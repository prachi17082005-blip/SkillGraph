from django.shortcuts import render


def home(request):
    return render(request, 'index.html')

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')