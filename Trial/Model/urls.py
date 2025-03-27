from django.urls import path
from .views import Calculator, past_projects, Results, Configure_Constants

app_name = 'Model'

urlpatterns = [
    path('Calculator/', Calculator, name='Calculator'),
    path('past-projects/', past_projects, name='past_projects'),
    path('Results/<int:emission_id>/', Results, name='Results'),
    path('Configure_Constants/', Configure_Constants, name='Configure_Constants'),
]