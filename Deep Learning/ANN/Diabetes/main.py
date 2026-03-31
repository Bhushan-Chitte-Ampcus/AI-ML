# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import pickle
# import tensorflow 
# from tensorflow import keras
# import pandas as pd

# app = FastAPI(title="Diabetes Prediction App")

# class Input(BaseModel):
#     pregnancies : int
#     glucose : int
#     bloodpressure : int
#     skinthickness : int
#     insulin : int
#     bmi : float
#     diabetespedigree : float
#     age : int

# try:
#     with open("./preprocessor.pkl", "rb") as f:
#         preprocessor = pickle.load(f)

#     model = keras.models.load_model("./indian_diabetes_ann.keras")
    
# except Exception as e:
#     raise HTTPException(status_code=404, detail="Model Not Loaded")


# @app.post("/predict")
# def get_prediction(user_input : Input):
#     user_input = pd.DataFrame([user_input.dict()])
#     pred = model.predict(preprocessor.transform(user_input))

#     if pred > 0.5:
#         return {"message" : "Diabetic"}
#     else:
#         return {"message" : "Non-Diabetic"}

# ----------------------------------------------------------------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import tensorflow 
from tensorflow import keras
import pandas as pd

app = FastAPI(title="Diabetes Prediction App")

# The middleware class that handles Cross-Origin Resource Sharing (CORS) in a FastAPI application. This middleware is essential for allowing a web browser running on one domain (origin) to make requests to your FastAPI API hosted on a different domain or port.
# CORS middleware to allow your HTML page to call the API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Input(BaseModel):
    pregnancies : int
    glucose : int
    bloodpressure : int
    skinthickness : int
    insulin : int
    bmi : float
    diabetespedigree : float
    age : int

try:
    with open("./preprocessor.pkl", "rb") as f:
        preprocessor = pickle.load(f)

    model = keras.models.load_model("./indian_diabetes_ann.keras")
    
except Exception as e:
    raise HTTPException(status_code=404, detail="Model Not Loaded")

@app.post("/predict")
def get_prediction(user_input : Input):
    user_input = pd.DataFrame([user_input.dict()])
    pred = model.predict(preprocessor.transform(user_input))

    if pred > 0.5:
        return {"message" : "Diabetic"}
    else:
        return {"message" : "Non-Diabetic"}