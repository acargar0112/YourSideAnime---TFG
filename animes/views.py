from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'animes/home.html')