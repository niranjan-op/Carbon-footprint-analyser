from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def Calculator(request):
    return render(request,'Calculator/Calculator.html')

def Configure_Constants(request):
    return render(request, 'Configure_Constants/Configure_Constants.html')

# Create your views here.
