from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
from tensorflow import keras
import numpy as np
import pandas as pd
from typing import Literal

app = FastAPI(title="Insurance Charges Prediction...")

class User_Input(BaseModel):
    age: int
    bmi: float
    children: int
    sex: Literal["male", "female"]
    smoker: Literal["yes", "no"]
    region: Literal["southwest", "southeast", "northwest", "northeast"]

try: 
    with open("./preprocessor.pkl", "rb") as f:
        preprocessor = pickle.load(f)
    
    model = keras.models.load_model("./insurance_ann.keras")

except Exception as e:
    raise HTTPException(status_code=500, detail="Model Not Loaded...")


@app.post("/predict")
def get_prediction(user_input : User_Input):
    user_input = pd.DataFrame([{
    "age": user_input.age,
    "bmi": user_input.bmi,
    "children": user_input.children,
    "sex": user_input.sex,
    "smoker": user_input.smoker,
    "region": user_input.region
    }])

    processed = preprocessor.transform(user_input)

    # if hasattr(processed, "toarray"):
    #     processed = processed.toarray()
    
    pred = model.predict(processed)

    return {
    "prediction": np.round(float(pred[0][0]), 2)
    }