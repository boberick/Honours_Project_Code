from fastapi import FastAPI
from pydantic import BaseModel
import xgboost as xgb
import pandas as pd
from datetime import datetime
import process_data
import train_model
from fastapi.middleware.cors import CORSMiddleware
from sklearn.preprocessing import LabelEncoder

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Load the saved model
model = xgb.XGBRegressor()
model.load_model('app_backend/web_app_model.json')

# Features used for prediction
features = ["Glucose", "Hour", "Minute", "Glucose_Level_Range", "Hour_sin", "Hour_cos","Minute_sin", "Minute_cos", 
            "Glucose_roll_mean", "Glucose_lag1", "Glucose_lag2", "Glucose_lag3", "Glucose_lag4"]

# List of target variables to predict
targets = ["Glucose_15min", "Glucose_30min", "Glucose_45min", "Glucose_60min"]

# Define the input data
class InputData(BaseModel):
    glucose: float
    datetime: datetime

@app.post("/predict")
async def predict(data: InputData):
    
    # Extract input data
    dateTime = data.datetime
    glucose_data = data.glucose
    
    # Process the input data
    process_data.process_data(dateTime, glucose_data)
    
    # Load the processed data
    df = pd.read_csv('app_backend/training_data.csv')

    # Encode the glucose level range variable so that the values become numerical
    label_encoder = LabelEncoder()
    df['Glucose_Level_Range'] = label_encoder.fit_transform(df['Glucose_Level_Range'])
    
    # Ensure the latest row includes all expected features
    latest_features = df.iloc[-1:][features].copy()
    
    # Ensure the input data is a 2D array for the model
    if len(latest_features.shape) == 1:
        latest_features = latest_features.values.reshape(1, -1)
    else:
        latest_features = latest_features.values
    
    # Store predictions
    predictions = {}

    # Get predictions for all targets at once
    all_preds = model.predict(latest_features)[0]

    for i, target in enumerate(targets):
        pred = float(all_preds[i])
        
        # Calculate error range 
        lower_bound = float(pred * 0.75)  
        upper_bound = float(pred * 1.25)  

        # Store predictions with error range
        predictions[target] = {
            "Prediction": pred,
            "Lower_Bound": lower_bound,
            "Upper_Bound": upper_bound
        }

    # Check if the data has 108 rows
    if df.shape[0] >= 16:
        
        # Load in dataset
        df = pd.read_csv('app_backend/training_data.csv')
        
        # Get rid of null values
        df.dropna(inplace=True)
        
        # Save the processed data
        df.to_csv('app_backend/training_data.csv', index=False)
        
        # Retrain the model
        train_model.train_model('app_backend/training_data.csv')
        
        # Reset the training data
        new_df = pd.DataFrame(columns=df.columns)
        new_df.to_csv('app_backend/training_data.csv', index=False)
        
    return predictions

# Run the API with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5000)