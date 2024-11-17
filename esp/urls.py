from django.urls import path
from .views import store_gps_data

urlpatterns = [
    path('store-gps_data/', store_gps_data, name='store_gps_data'),
]
