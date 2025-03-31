from django.shortcuts import render,redirect
def home(request):
    return render(request,"index.html")

# Create your views here.
def about_us(request):
    return render(request,"about_us.html")