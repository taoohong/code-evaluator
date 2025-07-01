from django.shortcuts import render


def index(request):
    # Page from the theme
    return render(request, 'index.html')
