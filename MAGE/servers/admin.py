from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter
from .models import GameServer, UT99Server, Q3AServer
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
        """
        Query the server via UDP to get server data
        :param obj: The current server object
        :return:
        """
        server_host_value = obj.server_host
        server_port_value = obj.server_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Create a socket connection
            sock.settimeout(1)  # Set a timeout for the socket

            # Construct the UQP query string
            query_string = "\\info\\"

            # Send the query to the server
            # UT99 UDP query uses gameport + 1
            sock.sendto(query_string.encode(), (server_host_value, int(server_port_value) + 1))

            # Receive and decode the response
            response, _ = sock.recvfrom(2048)
            response = response.decode("utf-8", errors="replace")

            # Parse the response and format to dict
            pairs = response.split('\\')[1:]
            result_dict = dict(zip(pairs[::2], pairs[1::2]))
            result_dict['status'] = 'Available'

            return result_dict

        except Exception as e:
            print(f"Error querying UT99 server: {str(e)}")
            sock.close()

            return {
                'status': 'Unreachable',
                'maptitle': 'N/A',
                'mapname': 'N/A',
                'gametype': 'N/A',
                'numplayers': 'N/A',
                'maxplayers': 'N/A'
            }

        finally:
            # Close the socket connection
            sock.close()

    def get_value_or_na(self, obj, key):
        server_data = self.query_server(obj)
        return server_data.get(key, 'N/A')


@admin.register(Q3AServer)
class Q3AServerAdmin(ServerChildAdmin):
    base_model = Q3AServer


@admin.register(GameServer)
class ServerParentAdmin(PolymorphicParentModelAdmin):
    base_model = GameServer
    child_models = (UT99Server, Q3AServer)
    list_display = ["server_name", "server_host"]
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
