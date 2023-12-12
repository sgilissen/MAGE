import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class ServerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

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
