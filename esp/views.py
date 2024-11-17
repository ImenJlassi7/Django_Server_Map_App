from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import GPSData  # Import the GPSData model
import json

@csrf_exempt
def store_gps_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        longitude = data.get("longitude")
        latitude = data.get("latitude")

        # Insert data into SQLite database using the GPSData model
        GPSData.objects.create(longitude=longitude, latitude=latitude)

        return JsonResponse({"status": "success", "message": "Data stored successfully"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
