import requests
import pandas as pd
import json
from datetime import datetime
import os
import logging
from config import Config

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s: %(message)s')

class EnvironmentalDataCollector:
    def __init__(self):
        self.openweather_key = Config.OPENWEATHER_API_KEY
        self.airvisual_key = Config.AIRVISUAL_API_KEY
        self.data_dir = 'data/raw'
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_openweather_data(self, city):
        """Fetch weather and pollution data from OpenWeatherMap"""
        try:
            # Fetch current weather and air pollution data
            weather_url = f"{Config.OPENWEATHER_BASE_URL}/weather"
            pollution_url = f"{Config.OPENWEATHER_BASE_URL}/air_pollution"
            
            weather_params = {
                'lat': city['lat'], 
                'lon': city['lon'], 
                'appid': self.openweather_key,
                'units': 'metric'
            }
            
            pollution_params = weather_params.copy()
            
            weather_response = requests.get(weather_url, params=weather_params)
            pollution_response = requests.get(pollution_url, params=pollution_params)
            
            weather_data = weather_response.json()
            pollution_data = pollution_response.json()
            
            return {
                'city': city['name'],
                'country': city['country'],
                'timestamp': datetime.utcnow().isoformat(),
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'wind_speed': weather_data['wind']['speed'],
                'aqi': pollution_data['list'][0]['main']['aqi'],
                'co': pollution_data['list'][0]['components']['co'],
                'no': pollution_data['list'][0]['components']['no'],
                'no2': pollution_data['list'][0]['components']['no2'],
                'o3': pollution_data['list'][0]['components']['o3'],
                'so2': pollution_data['list'][0]['components']['so2'],
                'pm2_5': pollution_data['list'][0]['components']['pm2_5'],
                'pm10': pollution_data['list'][0]['components']['pm10']
            }
        except Exception as e:
            logging.error(f"Error fetching OpenWeatherMap data for {city['name']}: {e}")
            return None

    def fetch_airvisual_data(self, city):
        """Fetch air quality data from AirVisual API"""
        try:
            url = f"{Config.AIRVISUAL_BASE_URL}/nearest_city"
            params = {
                'lat': city['lat'],
                'lon': city['lon'],
                'key': self.airvisual_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'success':
                return {
                    'city': city['name'],
                    'country': city['country'],
                    'timestamp': datetime.utcnow().isoformat(),
                    'aqi': data['data']['current']['pollution']['aqius'],
                    'main_pollutant': data['data']['current']['pollution']['mainus']
                }
        except Exception as e:
            logging.error(f"Error fetching AirVisual data for {city['name']}: {e}")
            return None

    def collect_data(self):
        """Collect data for all configured cities"""
        all_data = []
        
        for city in Config.CITIES:
            # Collect data from both APIs
            openweather_data = self.fetch_openweather_data(city)
            airvisual_data = self.fetch_airvisual_data(city)
            
            # Combine data
            if openweather_data and airvisual_data:
                combined_data = {**openweather_data, **airvisual_data}
                all_data.append(combined_data)
        
        # Create DataFrame and save
        if all_data:
            df = pd.DataFrame(all_data)
            filename = f"{self.data_dir}/environmental_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            logging.info(f"Data saved to {filename}")
            return filename
        
        logging.warning("No data collected")
        return None

# Script to run data collection
def main():
    collector = EnvironmentalDataCollector()
    data_file = collector.collect_data()
    
    if data_file:
        # DVC commands to version the data
        import subprocess
        
        # Add the new data file to DVC tracking
        subprocess.run(['/home/abdulrafay/.local/bin/dvc', 'add', data_file], check=True)
        
        # Commit changes
        subprocess.run(['/home/abdulrafay/.local/bin/dvc', 'commit'], check=True)
        
        # Push to remote storage
        subprocess.run(['/home/abdulrafay/.local/bin/dvc', 'push'], check=True)

if __name__ == '__main__':
    main()