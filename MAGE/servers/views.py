from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
import logging
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.template.defaulttags import register
from . import models
from .tasks import *
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, GroupSerializer

logger = logging.getLogger(__name__)


# Helper functions
def fetch_server_cached(server):
    """
    Fetch server from cache
    :param server: server object
    :return: JSON server data
    """
    # Get the server type from the model to cache it. This way we don't have to hardcode the cache identifier.
    server_type = ContentType.objects.get_for_model(server).model
    server_data = cache.get(f'gameserver-{server.pk}')

    # Server data is not cached. Perform asynchronous task to cache data.
    if server_data is None:
        # Match type of server
        match server_type:
            case "ut99server":
                query_ut99_server(server)
            case "q3aserver":
                query_q3a_server(server)
            case "ut2k4server":
                query_ut2k4_server(server)
            case "ut2k3server":
                # UT2k4 and UT2k3 use the same protocol
                query_ut2k4_server(server)
            case _:
                logger.info("Views: Unknown server type")

        server_data = {
            'server_type': server_type,
            'status_verbose': 'Polling server...',
            'status': 'server_polling',
            'maptitle': '-',
            'mapname': '-',
            'gametype': '-',
            'numplayers': '-',
            'maxplayers': '-'
        }
    else:
        server_data['server_type'] = server_type

    return server_data


# Helper classes
class ServerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows servers to be viewed
    """
    servers = {}
    for srv in models.GameServer.objects.all():
        server_data = fetch_server_cached(srv)
        servers[srv] = {
            "server_type": server_data['server_type'],
            "hostname": srv.server_host,
            "port": srv.server_port,
            "status_verbose": server_data['status_verbose'],
            "status": server_data['status'],
            "mapname": server_data['mapname'],
            "maptitle": server_data['maptitle'],
            "gametype": server_data['gametype'],
            "numplayers": server_data['numplayers'],
            "maxplayers": server_data['maxplayers'],
        }


def server_list(request):
    """
    Render homepage
    :param request:
    :return: template render
    """
    servers = {}
    for srv in models.GameServer.objects.all():
        server_data = fetch_server_cached(srv)
        servers[srv] = {
            "server_type": server_data['server_type'],
            "hostname": srv.server_host,
            "port": srv.server_port,
            "status_verbose": server_data['status_verbose'],
            "status": server_data['status'],
            "mapname": server_data['mapname'],
            "maptitle": server_data['maptitle'],
            "gametype": server_data['gametype'],
            "numplayers": server_data['numplayers'],
            "maxplayers": server_data['maxplayers'],
        }

    context = {
        'servers': servers,
        'name': "test"
    }

    return render(request=request, context=context, template_name="../../theme/templates/server_list.html")


def server_view(request, server_pk):
    current_user = request.user
    current_server = models.GameServer.objects.filter(pk=server_pk)[0]
    server_data = fetch_server_cached(current_server)

    context = {
        'server': {
            "server_type": server_data['server_type'],
            "hostname": current_server.server_host,
            "port": current_server.server_port,
            "status_verbose": server_data['status_verbose'],
            "status": server_data['status'],
            "mapname": server_data['mapname'],
            "maptitle": server_data['maptitle'],
            "gametype": server_data['gametype'],
            "numplayers": server_data['numplayers'],
            "maxplayers": server_data['maxplayers'],
        }
    }

    return render(request=request, context=context, template_name="../../theme/templates/server_view.html")

