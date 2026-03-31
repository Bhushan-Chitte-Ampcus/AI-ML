import numpy as np
import pickle
import streamlit as st
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


st.set_page_config(page_title="IMDB Sentiment Analysis", page_icon="🎬")
st.title("Sentiment Analysis App")

option = st.selectbox("choose an option", ["Traditional Machine Learning", "VADER"])
user_input = st.text_area("Enter your review here...")

if option == "Traditional Machine Learning":
    
    with open("../NLP/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    with open("../NLP/sentiment_analysis_model.pkl", "rb") as f:
        model = pickle.load(f)

    if st.button("Analyze Sentiment"):
        if user_input.strip() == "":
            st.warning("Please enter your review...")
        else:
            X = vectorizer.transform([user_input])
            pred = model.predict(X)
            pred_prob = model.predict_proba(X)[0]

            if pred == 1:
                st.success("Positive Sentiment")
                st.write(f"Confidence: {max(pred_prob)*100:.2f}%")
            else:
                st.error("Negative Sentiment")
                st.write(f"Confidence: {max(pred_prob)*100:.2f}%")

elif option == "VADER":
    if st.button("Analyze Sentiment"):
        if user_input.strip() == "":
            st.warning("Please enter your review...")
        else:
            analyzer = SentimentIntensityAnalyzer()
            sentiment_dict = analyzer.polarity_scores(user_input)

            if sentiment_dict['compound'] >= 0.05:
                st.success("Positive Sentiment")
            elif sentiment_dict['compound'] <= -0.05:
                st.error("Negative Sentiment")