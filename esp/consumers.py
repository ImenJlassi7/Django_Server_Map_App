import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GPSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def send_gps_data(self, latitude, longitude):
        await self.send(text_data=json.dumps({
            "latitude": latitude,
            "longitude": longitude
        }))
