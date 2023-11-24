from polymorphic.models import PolymorphicModel
from django.db import models


# Create a PolymorphicModel so we can subclass the various servers
# This requires django-polymorphic to be installed. This makes our job a bit easier.
class GameServer(PolymorphicModel):
    server_name = models.CharField(max_length=200)
    server_host = models.CharField(max_length=200)
    server_port = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Game Server"
        verbose_name_plural = "Game Servers"

    def __str__(self):
        return self.server_name


class UT99Server(GameServer):
    rcon_user = models.CharField(max_length=200, verbose_name="RCON Username")
    rcon_password = models.CharField(max_length=200, verbose_name="RCON Password")

    class Meta:
        verbose_name = "Unreal Tournament 99 Server"
        verbose_name_plural = "Unreal Tournament 99 Servers"

    def __str__(self):
        return self.server_name


class Q3AServer(GameServer):
    rcon_user = models.CharField(max_length=200, verbose_name="RCON Username")
    rcon_password = models.CharField(max_length=200, verbose_name="RCON Password")

    class Meta:
        verbose_name = "Quake 3 Arena Server"
        verbose_name_plural = "Quake 3 Arena Servers"

    def __str__(self):
        return self.server_name
