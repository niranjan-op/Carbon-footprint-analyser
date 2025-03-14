from django.urls import path,include
from django.contrib.auth import views as home_views
from . import views

urlpatterns=[
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),   
]