import pandas as pd
import numpy as np
import os

def process_data(dateTime, glucoseData):
    # Process the dateTime data
    time = pd.to_datetime(dateTime, format='%H:%M:%S')
    hour = time.hour
    minute = time.minute
    hourSin = np.sin(2 * np.pi * hour / 24.0)
    hourCos = np.cos(2 * np.pi * hour / 24.0)
    minuteSin = np.sin(2 * np.pi * minute / 60.0)
    minuteCos = np.cos(2 * np.pi * minute / 60.0)
    
    # Define glucose level thresholds
    glucose = glucoseData
    bins = [-float('inf'), 2.5, 5, 8, 10, float('inf')]
    labels = ['Very Low', 'Low', 'Normal', 'High', 'Very High']
    glucose_array = np.array([glucose])
    glucoseLevelRange = pd.cut(glucose_array, bins=bins, labels=labels)
    
    # Create a new row as a dictionary
    new_row = {
        'Time': time,
        'Glucose': glucose, 
        'Hour': hour, 
        'Minute': minute,
        'Glucose_Level_Range': glucoseLevelRange[0],  # Access the first element of the Series 
        'Hour_sin': hourSin, 
        'Hour_cos': hourCos,
        'Minute_sin': minuteSin,
        'Minute_cos': minuteCos
    }
    
    # Check if the training data file exists
    file_exists = os.path.isfile('app_backend/training_data.csv')
    
    # Load existing data or create an empty DataFrame
    if file_exists:
        df = pd.read_csv('app_backend/training_data.csv')
    else:
        # Define the columns for the initial DataFrame
        columns = [
            'Time', 'Glucose', 'Hour', 'Minute', 'Glucose_Level_Range', 'Hour_sin', 'Hour_cos', 'Minute_sin', 'Minute_cos',
            'Glucose_roll_mean','Glucose_lag1', 'Glucose_lag2', 'Glucose_lag3', 'Glucose_lag4',
            'Glucose_15min', 'Glucose_30min', 'Glucose_45min', 'Glucose_60min'
        ]
        df = pd.DataFrame(columns=columns)
    
    # Append the new row to the DataFrame
    df = df.append(new_row, ignore_index=True)
    
    # Rolling window features
    df["Glucose_roll_mean"] = df["Glucose"].rolling(window=5, min_periods=1).mean()  # Use min_periods to handle initial rows

    # Create attributes and values for future time-prediction modelling
    # Lag features are previous glucose values
    df["Glucose_lag1"] = df["Glucose"].shift(1)
    df["Glucose_lag2"] = df["Glucose"].shift(2)
    df["Glucose_lag3"] = df["Glucose"].shift(3)
    df["Glucose_lag4"] = df["Glucose"].shift(4)

    # Future glucose values
    df["Glucose_15min"] = df["Glucose"].shift(-1)  # 15 minutes ahead
    df["Glucose_30min"] = df["Glucose"].shift(-2)  # 30 minutes ahead
    df["Glucose_45min"] = df["Glucose"].shift(-3)  # 45 minutes ahead
    df["Glucose_60min"] = df["Glucose"].shift(-4)  # 60 minutes ahead
    
    # Save the updated data
    df.to_csv('app_backend/training_data.csv', index=False)