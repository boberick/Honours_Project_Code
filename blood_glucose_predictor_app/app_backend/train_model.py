import xgboost as xgb
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def train_model(input_file):
    
    # Load the saved model
    model = xgb.XGBRegressor()
    model.load_model("app_backend/web_app_model.json")

    # Load the data
    data = pd.read_csv(input_file)

    # Encode the glucose level range variable so that the values become numerical
    label_encoder = LabelEncoder()
    data['Glucose_Level_Range'] = label_encoder.fit_transform(data['Glucose_Level_Range'])

    # Split the data
    features = ["Glucose", "Hour", "Minute", "Glucose_Level_Range", "Hour_sin", "Hour_cos","Minute_sin", "Minute_cos", 
                "Glucose_roll_mean", "Glucose_lag1", "Glucose_lag2", "Glucose_lag3", "Glucose_lag4"]
    
    targets = ["Glucose_15min", "Glucose_30min", "Glucose_45min", "Glucose_60min"]

    # Train the model
    model.fit(data[features], data[targets])
    
    # Save the updated model
    model.save_model("app_backend/web_app_model.json")