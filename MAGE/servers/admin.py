from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter
from .models import GameServer, UT99Server, Q3AServer
from .tasks import query_ut99_server, query_q3a_server
from django.core.cache import cache
import socket
from django.utils.html import format_html


# Helper classes
class ServerMeta(type(admin.ModelAdmin)):
    def __new__(cls, name, bases, attrs):
        keys_to_display = ['status', 'maptitle', 'mapname', 'gametype', 'numplayers', 'maxplayers']

        for key in keys_to_display:
            method_name = f'display_server_{key}'

            def method(self, obj, key=key):
                return self.get_value_or_na(obj, key)

            attrs[method_name] = method
            attrs[method_name].short_description = f'Server {key.capitalize()}'

        return super().__new__(cls, name, bases, attrs)


# Register your models here.
class ServerChildAdmin(PolymorphicChildModelAdmin):
    """ Base model class for all child models """
    base_model = GameServer


@admin.register(UT99Server)
class UT99ServerAdmin(ServerChildAdmin, metaclass=ServerMeta):
    base_model = UT99Server
    list_display = ["server_name", "server_host", "server_port", "display_server_status",
                    "display_server_maptitle", "display_server_mapname", "display_server_gametype",
                    "display_server_numplayers", "display_server_maxplayers"]

    def query_server(self, obj):
        udp_data = cache.get(f'ut99-{obj.server_host}')

        # Server data is not cached. Perform asynchronous task to cache data.
        if udp_data is None:
            query_ut99_server(obj)
            udp_data = {
                'status': 'Polling server...',
                'maptitle': 'N/A',
                'mapname': 'N/A',
                'gametype': 'N/A',
                'numplayers': 'N/A',
                'maxplayers': 'N/A'
            }

        return udp_data

    def get_value_or_na(self, obj, key):
        server_data = self.query_server(obj)
        return server_data.get(key, 'N/A')


@admin.register(Q3AServer)
class Q3AServerAdmin(ServerChildAdmin, metaclass=ServerMeta):
    base_model = Q3AServer
    list_display = ["server_name", "server_host", "server_port", "display_server_status",
                    "display_server_maptitle", "display_server_mapname", "display_server_gametype",
                    "display_server_numplayers", "display_server_maxplayers"]

    def query_server(self, obj):
        udp_data = cache.get(f'q3a-{obj.server_host}')

        # Server data is not cached. Perform asynchronous task to cache data.
        if udp_data is None:
            query_q3a_server(obj)
            udp_data = {
                'status': 'Polling server...',
                'maptitle': 'N/A',
                'mapname': 'N/A',
                'gametype': 'N/A',
                'numplayers': 'N/A',
                'maxplayers': 'N/A'
            }

        return udp_data

    def get_value_or_na(self, obj, key):
        server_data = self.query_server(obj)
        return server_data.get(key, 'N/A')


@admin.register(GameServer)
class ServerParentAdmin(PolymorphicParentModelAdmin):
    base_model = GameServer
    child_models = (UT99Server, Q3AServer)
    list_display = ["server_name", "server_host"]
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
