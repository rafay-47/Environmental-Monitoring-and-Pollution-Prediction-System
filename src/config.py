import os

class Config:
    # OpenWeatherMap API Configuration
    OPENWEATHER_API_KEY = 'ad7c8a4c5acee57ea52b702c6d27aba2'
    OPENWEATHER_BASE_URL = 'http://api.openweathermap.org/data/2.5'
    
    # AirVisual (IQAir) API Configuration
    AIRVISUAL_API_KEY = '9e7a3411-b9ee-431b-8cd7-f3d0288a5a06'
    AIRVISUAL_BASE_URL = 'https://api.airvisual.com/v2'
    
    # Cities to monitor (example locations)
    CITIES = [
        {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060, 'country': 'US'},
        {'name': 'London', 'lat': 51.5074, 'lon': -0.1278, 'country': 'GB'},
        {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503, 'country': 'JP'}
    ]
