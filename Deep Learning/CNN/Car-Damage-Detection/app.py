import streamlit as st
import numpy as np
import cv2
from tensorflow import keras
from PIL import Image

# Load model
def load_model():
    model = keras.models.load_model("./custom-cnn-with-augmentation.keras")
    return model

model = load_model()

# Set image size (must match training)
img_width, img_height = 64, 64

st.title("Car Damage Detection App")

st.write("Upload a car image to check whether it is **Damaged** or **Whole**.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file).convert("L")  # Convert to grayscale
    st.image(image, caption="Uploaded Image", width="stretch")

    # Convert to numpy array
    img = np.array(image)

    # Resize
    img = cv2.resize(img, (img_width, img_height))

    # Normalize
    img = img / 255.0

    # # Add channel dimension
    # img = np.expand_dims(img, axis=-1)

    # # Add batch dimension
    # img = np.expand_dims(img, axis=0)
    
    img = img.reshape((1, img_width, img_height, 1))

    # Predict
    pred = model.predict(img)
    pred_class = np.argmax(pred, axis=1)

    # Output result
    if pred_class[0] == 0:
        st.error("Result: Damage Detected")
    else:
        st.success("Result: Car is Whole (No Damage)")

