import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import asyncio
from . import models
from django.core.cache import cache
from .tasks import query_ut99_server, query_q3a_server, query_ut2k4_server
from channels.db import database_sync_to_async
import os

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
                logger.warning("Consumers: Unknown server type")

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


def image_exists(image_filename):
    # Construct the local path from the image filename and STATIC_ROOT
    local_path = os.path.join(settings.STATIC_ROOT, image_filename)

    # Check if the file exists on the server
    return os.path.exists(local_path)


class ServerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        server_data = await self.fetch_server_data()
        data_refresh_timer = 30
        ws_data = {
            'refresh_timer': data_refresh_timer,
            'server_data': server_data
        }

        while True:
            await asyncio.sleep(data_refresh_timer)
            await self.send(json.dumps(ws_data))

    @database_sync_to_async
    def fetch_server_data(self):
        """
        Fetches server objects from the DB, checks if there's cached info and queries servers if necessary
        :return:
        """
        servers = models.GameServer.objects.all()
        server_data = {}
        for srv in servers:
            cur_srv_data = fetch_server_cached(srv)
            # Internal MAGE name. Not fetched from the server cache, but are included to identify the servers
            # within the backend, and used in the frontend in the server listing.
            server_data[str(srv.pk)] = {}
            server_data[str(srv.pk)]['mage_servername'] = str(srv)
            server_data[str(srv.pk)]['server_info'] = cur_srv_data
            server_data[str(srv.pk)]['server_host'] = srv.server_host
            server_data[str(srv.pk)]['server_port'] = srv.server_port

            # Check if the map image exists in staticfiles
            mapimg_filename = f"img/maps/{cur_srv_data['server_type']}/{cur_srv_data['mapname']}.jpg"
            if not image_exists(mapimg_filename):
                mapimg_filename = "img/maps/nomap.jpg"

            server_data[str(srv.pk)]['server_info']['mapimg'] = mapimg_filename


        return server_data

    async def disconnect(self, code):
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        expression = text_data_json['expression']
        try:
            result = eval(expression)
        except Exception as e:
            logger.exception(f'WS: ServerConsumer: Invalid expression: {e}')
            result = "Invalid Expression"
        await self.send(text_data=json.dumps({'result': result}))
