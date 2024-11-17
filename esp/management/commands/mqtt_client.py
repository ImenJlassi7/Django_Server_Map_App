import json
import websocket
import paho.mqtt.client as mqtt  # type: ignore
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from esp.models import GPSData  # Adjust according to your app name
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Command(BaseCommand):
    help = "Starts MQTT client to receive GPS data from ESP32 and save to MongoDB and SQLite"

    def handle(self, *args, **options):
        # MongoDB connection
        mongo_client = MongoClient("mongodb+srv://Imen77:lBMe4mmUcSxjcP9a@cluster0.qqi6fog.mongodb.net/lessonPlansDB?retryWrites=true&w=majority")
        db = mongo_client["gps_data"]
        collection = db["gps"]

        # Set up WebSocket client
        def on_message(ws, message):
            print(f"Message from WebSocket server: {message}")

        def on_error(ws, error):
            print(f"Error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("WebSocket connection closed")

        def on_open(ws):
            print("WebSocket connected")

        # WebSocket URL (replace with your WebSocket server address)
        ws_url = "ws://192.168.74.238:8080"  # Make sure this is the same address used in your Flutter app

        # Create WebSocket connection
        ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
        
        # Start WebSocket in a background thread
        import threading
        threading.Thread(target=ws.run_forever).start()

        # MQTT functions
        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT broker with result code " + str(rc))
            client.subscribe("imen/location/gps")  # Subscribe to the relevant MQTT topic

        def on_message(client, userdata, msg):
            try:
                data = json.loads(msg.payload.decode())
                latitude = data.get("latitude")
                longitude = data.get("longitude")

                # Save to MongoDB
                collection.insert_one({"latitude": latitude, "longitude": longitude})

                # Save to SQLite
                GPSData.objects.create(latitude=latitude, longitude=longitude)

                # Send data to WebSocket
                if ws and ws.sock and ws.sock.connected:
                    gps_data = json.dumps({
                        'latitude': latitude,
                        'longitude': longitude
                    })
                    ws.send(gps_data)

                # Forward data to Django WebSocket channel layer
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(  # Send the data to the group
                    "gps_data",
                    {
                        "type": "send_gps_data",
                        "latitude": latitude,
                        "longitude": longitude
                    }
                )

            except Exception as e:
                print(f"Error processing message: {e}")

        # Setup MQTT client
        client = mqtt.Client()
        client.username_pw_set("imen", "123456789")
        client.on_connect = on_connect
        client.on_message = on_message

        client.tls_set()
        client.connect("905976ca2340485f91499409413898b7.s1.eu.hivemq.cloud", 8883, 60)

        # Start the MQTT loop
        client.loop_forever()
