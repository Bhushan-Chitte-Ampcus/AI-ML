import numpy as np
import pandas as pd
import pickle 
import streamlit as st
from sklearn.preprocessing import StandardScaler


st.title("Wine Quality Prediction")
st.write("This app predicts the quality of wine based on its chemical properties.")

with st.form("prediction form"):
    col1, col2 = st.columns(2)

    with col1:
        fixed_acidity = st.number_input("Fixed Acidity", min_value=0.0, max_value=15.0)
        volatile_acidity = st.number_input("Volatile Acidity", min_value=0.0, max_value=2.0)
        citric_acid = st.number_input("Citric Acid", min_value=0.0, max_value=2.0)
        residual_sugar = st.number_input("Residual Sugar", min_value=0.0, max_value=35.0)
        chlorides = st.number_input("Chlorides", min_value=0.0, max_value=1.0)
        free_sulfur_dioxide = st.number_input("Free Sulfur Dioxide", min_value=0.0, max_value=150.0)

    with col2:
        total_sulfur_dioxide = st.number_input("Total Sulfur Dioxide", min_value=0.0, max_value=375.0)
        density = st.number_input("Density", min_value=0.0, max_value=2.0)
        ph = st.number_input("pH", min_value=0.0, max_value=14.0)
        sulphate = st.number_input("Sulphate", min_value=0.0, max_value=2.0)
        alcohol = st.number_input("Alcohol", min_value=0.0, max_value=20.0)
        quality = st.number_input("Quality", min_value=3, max_value=9)

    submit_button = st.form_submit_button("Predict Quality")

    with open("./wine_type_xgb_model.pkl", "rb") as f:
        model = pickle.load(f)

    if submit_button and model is not None:
        input_data = np.array([[fixed_acidity, volatile_acidity, citric_acid, residual_sugar, chlorides, free_sulfur_dioxide, total_sulfur_dioxide, density, ph, sulphate, alcohol, quality]])
        df = pd.DataFrame(input_data)
        df_scaled = StandardScaler().fit_transform(df)

        try:
            prediction = model.predict(df_scaled)
            st.success(f"Predicted Wine Type: {['Red' if prediction[0] == 1 else 'White'][0]}")
        except Exception as e:
            st.error(f"Error in prediction: {e}")


    