import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer


class DataLoader:
    @staticmethod
    def load_all_csv_files(directory):
        """
        Load all CSV files from the specified directory
        
        :param directory: Path to the directory containing CSV files
        :return: Concatenated DataFrame of all CSV files
        """
        # List all CSV files in the directory
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        
        # Check if any files exist
        if not csv_files:
            raise ValueError(f"No CSV files found in {directory}")
        
        # Read and concatenate all CSV files
        dataframes = []
        for file in csv_files:
            file_path = os.path.join(directory, file)
            try:
                df = pd.read_csv(file_path)
                dataframes.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
        
        # Combine all dataframes
        combined_df = pd.concat(dataframes, ignore_index=True)
        
        return combined_df

def preprocess_data(df):
    """
    Preprocess environmental data.
    
    Args:
        df (pandas.DataFrame): Input dataframe
    
    Returns:
        pandas.DataFrame: Preprocessed data
    """
    # Features and target
    features = ['temperature', 'humidity', 'wind_speed', 'co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10']
    target = 'aqi'
    
    # Create a copy of the dataframe
    df_processed = df.copy()
    
    # Handle missing values
    for column in features + [target]:
        # Fill missing values with median
        df_processed[column].fillna(df_processed[column].median(), inplace=True)
    
    # Remove outliers using Interquartile Range (IQR) method for each feature
    for column in features + [target]:
        Q1 = df_processed[column].quantile(0.25)
        Q3 = df_processed[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Filter out outliers
        df_processed = df_processed[
            (df_processed[column] >= lower_bound) & 
            (df_processed[column] <= upper_bound)
        ]
    
    return df_processed

# def feature_engineering(df):
#     """
#     Create additional features for time series prediction.
    
#     Args:
#         df (pandas.DataFrame): Preprocessed dataframe
    
#     Returns:
#         pandas.DataFrame: Dataframe with engineered features
#     """
#     # Create lagged features for each input feature
#     features = ['temperature', 'humidity', 'wind_speed', 'co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10']
#     target = 'aqi'
    
#     # Create a copy of the dataframe
#     df_engineered = df.copy()
    
#     # Create lag features
#     for feature in features:
#         df_engineered[f'{feature}_lag1'] = df_engineered[feature].shift(1)
#         df_engineered[f'{feature}_lag2'] = df_engineered[feature].shift(2)
    
#     # Drop rows with NaN values created by lag features
#     df_engineered.dropna(inplace=True)
    
#     return df_engineered