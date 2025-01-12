# model_save.py
import joblib
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import traceback



app = Flask(__name__)

def load_model(filename='../models/model.pkl'):
    try:
        # Load model with more detailed error handling
        with open(filename, 'rb') as f:
            model_data = joblib.load(f)
        
        # Validate model data
        if not model_data or 'model' not in model_data:
            raise ValueError("Invalid model data structure")
        
        return model_data
    except Exception as e:
        print(f"Comprehensive model loading error: {e}")
        return None
    
@app.route('/prediction', methods=['POST'])
def predict_aqi():
    try:
        # Load the ARIMA model
        model_data = load_model()
        if not model_data:
            return jsonify({"error": "Could not load model"}), 500
        
        # Extract ARIMA model
        model = model_data['model']
        model_order = model_data['order']
        
        try:
            # Forecast next AQI value
            forecast = model.get_forecast(steps=1)
            
            predicted_mean = float(forecast.predicted_mean.values[0])
            conf_int = forecast.conf_int(alpha=0.05)
            
            return jsonify({
                "predicted_aqi": predicted_mean,
                "prediction_interval_lower": float(conf_int.values[0][0]),
                "prediction_interval_upper": float(conf_int.values[0][1]),
                "model_order": model_order
            })
        
        except Exception as forecast_error:
            return jsonify({
                "error": f"Prediction failed: {str(forecast_error)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "error": f"Unexpected error: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API is running.
    """
    example_prediction_usage()
    return jsonify({"status": "healthy"}), 200

def example_prediction_usage():
    """
    Example script demonstrating how to use the prediction API
    """
    import requests
    
    # API endpoint
    url = 'http://localhost:8000/prediction'
    
    
    # Send POST request
    response = requests.post(url)
    
    # Print response
    print("Prediction Response:")
    print(response.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    
