from django.urls import path,include
from django.contrib.auth import views as home_views
from . import views
urlpatterns = [
      path('', views.home, name='home'),
    path("about_us/",views.about_us,name="about_us"),
]