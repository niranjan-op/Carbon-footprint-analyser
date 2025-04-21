from django.shortcuts import render,redirect
def home(request):
    return render(request, "home.html")

# Create your views here.
def about_us(request):
    return render(request,"about_us.html")

def contactus(request):
    return render(request, "contactus.html")