from fastapi import FastAPI, File, UploadFile
import numpy as np
from PIL import Image
from tensorflow import keras
import cv2
import io

app = FastAPI(title="Car Damage Detection Endpoint")

model = keras.models.load_model("../custom-cnn-with-augmentation.keras")

def predict(image: Image.Image):
    img = np.array(image)

    # Resize
    img = cv2.resize(img, (64, 64))

    # Normalize
    img = img / 255.0

    # If RGB → keep 3 channels
    img = img.reshape((1, 64, 64, 1))

    # Predict
    pred = model.predict(img)
    pred_class = np.argmax(pred, axis=1)

    if pred_class[0] == 0:
        return {"result": "Damage Detected"}
    else:
        return {"result": "Car is Whole (No Damage)"}


@app.post("/predict")
async def get_prediction(image: UploadFile = File(...)):
    contents = await image.read()
    img = Image.open(io.BytesIO(contents)).convert("L")

    pred = predict(img)
    return pred

