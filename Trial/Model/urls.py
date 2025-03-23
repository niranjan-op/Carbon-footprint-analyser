from django.urls import path
from . import views

app_name = 'Model'

urlpatterns = [
    path("Calculator/", views.Calculator, name='Calculator'),
    path("Configure_Constants/", views.Configure_Constants, name='Configure_Constants'),
    path('get-explosives/', views.get_explosives, name='get_explosives'),
    path('get-transports/', views.get_transports, name='get_transports'),
    path('projects/', views.project_history, name='project_history'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project-history/', views.project_history, name='project_history'),
]