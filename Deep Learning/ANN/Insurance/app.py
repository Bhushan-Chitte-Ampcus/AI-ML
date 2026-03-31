import streamlit as st
import numpy as np
import pandas as pd
import joblib
from tensorflow import keras

# Load model & preprocessor
model = keras.models.load_model("./insurance_ann.keras")
preprocessor = joblib.load("./preprocessor.pkl")

st.title("Insurance Cost Prediction App")

st.write("Enter details to predict medical insurance charges")

# User Inputs
age = st.slider("Age", 18, 100, 30)
bmi = st.slider("BMI", 10.0, 50.0, 25.0)
children = st.slider("Number of Children", 0, 5, 0)

sex = st.selectbox("Sex", ["male", "female"])
smoker = st.selectbox("Smoker", ["yes", "no"])
region = st.selectbox("Region", ["northeast", "northwest", "southeast", "southwest"])

# Convert to DataFrame
input_data = pd.DataFrame({
    "age": [age],
    "bmi": [bmi],
    "children": [children],
    "sex": [sex],
    "smoker": [smoker],
    "region": [region]
})

# Preprocess
input_processed = preprocessor.transform(input_data)

# Predict
if st.button("Predict Insurance Cost"):
    prediction = model.predict(input_processed)
    st.success(f"Estimated Insurance Cost: {prediction[0][0]:,.2f}")