from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter
from .models import GameServer, UT99Server, Q3AServer
from .tasks import query_ut99_server, query_q3a_server
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
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
        # Get the server type from the model to cache it. This way we don't have to hardcode the cache identifier.
        server_type = ContentType.objects.get_for_model(obj).model
        server_data = cache.get(f'{server_type}-{obj.server_host}')

        # Server data is not cached. Perform asynchronous task to cache data.
        if server_data is None:
            query_ut99_server(obj)
            server_data = {
                'status': 'Polling server...',
                'maptitle': 'N/A',
                'mapname': 'N/A',
                'gametype': 'N/A',
                'numplayers': 'N/A',
                'maxplayers': 'N/A'
            }

        return server_data

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
        # Get the server type from the model to cache it. This way we don't have to hardcode the cache identifier.
        server_type = ContentType.objects.get_for_model(obj).model
        server_data = cache.get(f'{server_type}-{obj.server_host}')

        # Server data is not cached. Perform asynchronous task to cache data.
        if server_data is None:
            query_q3a_server(obj)
            server_data = {
                'status': 'Polling server...',
                'maptitle': 'N/A',
                'mapname': 'N/A',
                'gametype': 'N/A',
                'numplayers': 'N/A',
                'maxplayers': 'N/A'
            }

        return server_data

    def get_value_or_na(self, obj, key):
        server_data = self.query_server(obj)
        return server_data.get(key, 'N/A')


@admin.register(GameServer)
class ServerParentAdmin(PolymorphicParentModelAdmin):
    base_model = GameServer
    child_models = (UT99Server, Q3AServer)
    list_display = ["server_name", "server_host"]
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
