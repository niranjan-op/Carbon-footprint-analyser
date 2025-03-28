from django.urls import path
from .views import Calculator, past_projects, Results, Configure_Constants, delete_project

app_name = 'Model'

urlpatterns = [
    path('Calculator/', Calculator, name='Calculator'),
    path('past-projects/', past_projects, name='past_projects'),
    path('Results/<str:project_name>/', Results, name='Results'),
    path('Configure_Constants/', Configure_Constants, name='Configure_Constants'),
    path('delete-project/<str:project_name>/', delete_project, name='delete_project'),
]