from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
from tensorflow import keras
import pandas as pd

app = FastAPI(title="Graduate Admission Prediction App")

class Input(BaseModel):
    GRE Score : int
    toefl_score : int
    university_rating : int
    sop : float
    lor : float
    cgpa : float
    research : int

try:
    with open("./preprocessor.pkl", "rb") as f:
        preprocessor = pickle.load(f)

    model = keras.models.load_model("./graduate_ann.keras")

except Exception as e:
    raise HTTPException(status_code=404, detail="Model not loaded...")


@app.post("/predict")
def get_prediction(user_input : Input):
    user_input = pd.DataFrame([user_input.dict()])
    pred = model.predict(preprocessor.transform(user_input))

    return {
        "prediction" : pred
    }