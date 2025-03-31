from django.urls import path
from .views import Calculator, past_projects, Results, Configure_Constants, delete_project

app_name = 'Model'

urlpatterns = [
    path('Calculator/', Calculator, name='Calculator'),
    path('past-projects/', past_projects, name='past_projects'),
    path('Results/<str:financial_year>/', Results, name='Results'),
    path('Configure_Constants/', Configure_Constants, name='Configure_Constants'),
    path('delete-project/<str:financial_year>/', delete_project, name='delete_project'),
]