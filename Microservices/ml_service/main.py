from fastapi import FastAPI, HTTPException
import pickle

app = FastAPI(title="ML Services - Sentiment Analysis")

try:
    with open("./vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    with open("./sentiment_analysis_model.pkl", "rb") as f:
        model = pickle.load(f)

except Exception as e:
    raise HTTPException(status_code=404, detail="Model not loaded")

@app.get("/health")
def health():
    return {"status": "ML service is running"}

@app.post("/predict")
def predict(text: str):
    X = vectorizer.transform([text])
    prediction = model.predict(X)
    
    if prediction == 1:
        return {"success": "positive sentiment"}
    else:
        return {"error": "negative sentiment"}