import pickle
import pandas as pd

# import the ml model
with open('./model/model.pkl', 'rb') as f:
    model = pickle.load(f)

# MLFLOW
MODEL_VERSION = "1.0.0"

class_labels = model.classes_.tolist()

def predict_output(user_input : dict):
    input_df = pd.DataFrame([user_input])
    
    predicted_class = model.predict(input_df)[0]
    
    probabilities = model.predict_proba(input_df)[0]
    confidence = max(probabilities)

    class_probs = dict(zip(class_labels, [round(p, 4) for p in probabilities]))
    
    return {
        "predicted_category" : predicted_class,
        "confidence" : round(confidence, 4),
        "class_probabilies" : class_probs
    }

