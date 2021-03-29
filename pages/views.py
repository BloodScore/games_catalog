# from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def detailed_page(request):
    return render(request, 'detailed_page.html')
