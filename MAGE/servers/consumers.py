import json
from channels.generic.websocket import WebsocketConsumer


class ServerConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        self.close()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        expression = text_data_json['expression']
        try:
            result = eval(expression)
        except Exception as e:
            result = "Invalid Expression"
        self.send(text_data=json.dumps({'result': result}))
