from django.urls import path
from . import views

app_name = 'Model'  # Add this line

urlpatterns = [
    path("Calculator/", views.Calculator, name='Calculator'),
    path("Configure_Constants/", views.Configure_Constants, name='Configure_Constants'),
    path("Results/", views.Results, name='Results'),
]