from django.urls import include, path
from rest_framework import routers
from . import views

app_name = "servers"


urlpatterns = [
    path("", views.homepage, name="homepage"),
]