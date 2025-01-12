import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.tsa.arima.model import ARIMA
import warnings
from data_preprocessing import DataLoader, preprocess_data
import itertools

warnings.filterwarnings("ignore")


def train_arima_model(data, order=(1,1,1), tune_hyperparameters=True):
    """
    Train ARIMA model with optional hyperparameter tuning and MLflow tracking.
    
    Args:
        data (pandas.Series): Time series AQI data
        order (tuple, optional): Initial ARIMA model order (p,d,q)
        tune_hyperparameters (bool, optional): Whether to perform grid search
    
    Returns:
        tuple: Best model, best predictions, best test data, and best parameters
    """
    # Split data into train and test sets
    train_size = int(len(data) * 0.8)
    train, test = data[:train_size], data[train_size:]
    
    # Hyperparameter tuning configuration
    if tune_hyperparameters:
        # Define hyperparameter search space
        p = range(0, 3)  # AR terms
        d = range(0, 2)  # Differencing
        q = range(0, 3)  # MA terms
        
        # Generate all possible parameter combinations
        pdq = list(itertools.product(p, d, q))
        
        # Track best model and metrics
        best_rmse = float('inf')
        best_model = None
        best_predictions = None
        best_order = None
        
        # Main MLflow run to track overall hyperparameter tuning
        with mlflow.start_run(run_name="ARIMA_Hyperparameter_Tuning"):
            # Grid search through different ARIMA configurations
            for param in pdq:
                # Create a nested run for each parameter configuration
                with mlflow.start_run(nested=True):
                    try:
                        # Train model with current parameters
                        model = ARIMA(train, order=param)
                        model_fit = model.fit()
                        
                        # Make predictions
                        predictions = model_fit.forecast(steps=len(test))
                        
                        # Calculate metrics
                        mse = mean_squared_error(test, predictions)
                        rmse = np.sqrt(mse)
                        mae = mean_absolute_error(test, predictions)
                        
                        # Log parameters for this specific run
                        mlflow.log_params({
                            'arima_p': param[0],
                            'arima_d': param[1],
                            'arima_q': param[2]
                        })
                        
                        # Log metrics for this run
                        mlflow.log_metrics({
                            'rmse': rmse,
                            'mae': mae
                        })
                        
                        # Update best model if current model performs better
                        if rmse < best_rmse:
                            best_rmse = rmse
                            best_model = model_fit
                            best_predictions = predictions
                            best_order = param
                    
                    except Exception as e:
                        # Log the error for the specific parameter configuration
                        mlflow.log_param('error', str(e))
                        print(f"Error with parameters {param}: {e}")
            
            # Log the best model details in the main run
            if best_model:
                mlflow.log_param('best_arima_order', best_order)
                mlflow.log_metric('best_rmse', best_rmse)
                mlflow.sklearn.log_model(best_model, 'best_arima_model')
                
                return best_model, best_predictions, test, best_order
        
        # If no valid model found
        raise ValueError("No valid ARIMA model configuration found during hyperparameter tuning.")
    
    # If no hyperparameter tuning, use default approach
    else:
        with mlflow.start_run():
            # Train ARIMA model with provided order
            model = ARIMA(train, order=order)
            model_fit = model.fit()
            
            # Make predictions
            predictions = model_fit.forecast(steps=len(test))
            
            # Calculate evaluation metrics
            mse = mean_squared_error(test, predictions)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(test, predictions)
            
            # Log parameters and metrics
            mlflow.log_param('arima_order', order)
            mlflow.log_metric('test_rmse', rmse)
            mlflow.log_metric('test_mae', mae)
            
            # Log model
            mlflow.sklearn.log_model(model_fit, 'arima_model')
            
            return model_fit, predictions, test, order

# Example usage
# data = pd.Series(...)  # Your time series data
# best_model, best_predictions, test_data, best_order = train_arima_model(data)
    
def save_best_model(model, order, filename='../models/model.pkl'):
    """
    Save the best ARIMA model to a pickle file.
    
    Args:
        model: Trained ARIMA model
        filename (str): Filename to save the model
    
    Returns:
        str: Path to the saved model
    """
    try:
        # Extract model parameters and results
        model_data = {
            'order': order,
            'model': model
        }
        
        # Save the model
        joblib.dump(model_data, filename)
        print(f"Model saved successfully to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving model: {e}")
        return None

def main():
    # Set up MLflow tracking
    #mlflow.set_tracking_uri('file:///mlruns')
    mlflow.set_experiment('aqi_prediction')
    
    # Load and preprocess data
    raw_data_dir = '../data/raw/'
    df = DataLoader.load_all_csv_files(raw_data_dir)
    
    if df is not None:
        # Preprocess the data
        df_processed = preprocess_data(df)
        
        # Feature engineering
        #df_engineered = feature_engineering(df_processed)
        
        # Select target variable
        aqi_data = df_processed['aqi']
        
        # Try multiple ARIMA model orders
        orders_to_try = [
            (1,1,1),
            (1,0,1),
            (2,1,2)
        ]
        
        best_model = None
        best_order = None
        best_rmse = float('inf')
        
        for order in orders_to_try:
            model, predictions, test, order = train_arima_model(aqi_data, order)
            
            rmse = np.sqrt(mean_squared_error(test, predictions))
            
            if rmse < best_rmse:
                best_rmse = rmse
                best_model = model
                best_order = order
        
        print(f"Best ARIMA Model Order: {best_order}")
        print(f"Best RMSE: {best_rmse}")
        save_best_model(best_model, best_order)
    else:
        print("Failed to load and process data.")

if __name__ == '__main__':
    main()