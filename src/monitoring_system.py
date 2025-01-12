from prometheus_client import start_http_server, Gauge, Counter
from prometheus_client import PLATFORM_COLLECTOR, PROCESS_COLLECTOR, GC_COLLECTOR
import time
import random
import requests
import threading

# Disable default collectors to reduce noise
PLATFORM_COLLECTOR.collect = lambda: []
PROCESS_COLLECTOR.collect = lambda: []
GC_COLLECTOR.collect = lambda: []

# Metrics for Data Ingestion
DATA_INGESTION_LATENCY = Gauge(
    'environmental_data_ingestion_latency_seconds', 
    'Latency of data ingestion from different sources',
    ['source']
)
DATA_INGESTION_VOLUME = Counter(
    'environmental_data_ingestion_volume_total', 
    'Total volume of data ingested from different sources',
    ['source']
)

# Metrics for Model Prediction
MODEL_PREDICTION_LATENCY = Gauge(
    'aqi_prediction_latency_seconds', 
    'Latency of AQI prediction'
)
MODEL_PREDICTION_ACCURACY = Gauge(
    'aqi_prediction_accuracy_percentage', 
    'Accuracy of AQI predictions'
)

# Metrics for API Performance
API_REQUEST_COUNTER = Counter(
    'aqi_api_requests_total', 
    'Total number of API requests'
)
API_ERROR_COUNTER = Counter(
    'aqi_api_errors_total', 
    'Total number of API errors'
)

class EnvironmentalMonitoring:
    def __init__(self, api_url):
        self.api_url = api_url
    
    def simulate_data_ingestion(self):
        while True:
            try:
                sources = ['OpenWeatherMap', 'AirVisual']
                for source in sources:
                    start_time = time.time()
                    
                    time.sleep(random.uniform(0.1, 1.0))
                    
                    latency = time.time() - start_time
                    DATA_INGESTION_LATENCY.labels(source=source).set(latency)
                    DATA_INGESTION_VOLUME.labels(source=source).inc(random.randint(100, 1000))
            
            except Exception as e:
                print(f"Data ingestion error: {e}")
            
            time.sleep(5)
    
    def monitor_api_performance(self):
        while True:
            try:
                API_REQUEST_COUNTER.inc()
                
                start_time = time.time()
                response = requests.post(self.api_url)
                
                latency = time.time() - start_time
                MODEL_PREDICTION_LATENCY.set(latency)
                
                if response.status_code == 200:
                    prediction = response.json().get('predicted_aqi', 0)
                    print(f"Predicted AQI: {prediction}")
                    MODEL_PREDICTION_ACCURACY.set(prediction)
                else:
                    API_ERROR_COUNTER.inc()
                    print(f"API Error: {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                API_ERROR_COUNTER.inc()
                print(f"API Request Error: {e}")
            
            time.sleep(5)
    
    def start_monitoring(self):
        # Start Prometheus metrics server
        start_http_server(9000)
        
        # Create and start monitoring threads
        data_ingestion_thread = threading.Thread(target=self.simulate_data_ingestion, daemon=True)
        api_monitor_thread = threading.Thread(target=self.monitor_api_performance, daemon=True)
        
        data_ingestion_thread.start()
        api_monitor_thread.start()
        
        # Keep main thread running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping monitoring...")

def main():
    API_URL = 'http://localhost:8000/prediction'
    monitor = EnvironmentalMonitoring(API_URL)
    monitor.start_monitoring()

if __name__ == '__main__':
    main()