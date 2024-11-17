from django.contrib import admin
from .models import GPSData

@admin.register(GPSData)
class GPSDataAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'timestamp')
    ordering = ('-timestamp',)
