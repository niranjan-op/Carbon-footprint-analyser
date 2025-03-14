from django.urls import path,include
from django.contrib.auth import views as home_views
from . import views
urlpatterns = [
    path("",views.blogs,name="Blogs"),
]