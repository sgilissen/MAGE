from django.urls import include, path
from rest_framework import routers
from . import views


app_name = "servers"


urlpatterns = [
    path("", views.server_list, name="servers"),
    path("<server_pk>/", views.server_view, name="server_view")
]