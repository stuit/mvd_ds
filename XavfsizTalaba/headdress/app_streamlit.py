import streamlit as st
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np


np.set_printoptions(suppress=True)
st.set_page_config(page_title="Headwear Classifier", page_icon="👒", layout="centered")

st.title("Headwear Classifier")
st.markdown("Upload an image to classify headwear (hijab, hat, or hair).")
@st.cache_resource
def load_keras_model():
    try:
        model = load_model("keras_model.h5", compile=False)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_keras_model()
try:
    with open("labels.txt", "r") as f:
        class_names = [line.strip()[2:] for line in f.readlines()] 
except FileNotFoundError:
    st.error("labels.txt not found. Please ensure it exists in the project directory.")
    class_names = []


uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)
    try:
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)


        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1


        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array

        if model is not None:
            with st.spinner("Classifying..."):
                prediction = model.predict(data)
                index = np.argmax(prediction)
                class_name = class_names[index] if index < len(class_names) else "Unknown"
                confidence_score = float(prediction[0][index])

            st.success("Prediction Complete!")
            st.write(f"**Class**: {class_name}")
            st.write(f"**Confidence Score**: {confidence_score:.4f}")
            st.write("**Raw Probabilities**:")
            for i, (name, prob) in enumerate(zip(class_names, prediction[0])):
                st.write(f"- {name}: {prob:.4f}")
        else:
            st.error("Model not loaded. Cannot make predictions.")
    except Exception as e:
        st.error(f"Error processing image: {e}")