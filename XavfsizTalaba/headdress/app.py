from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import uvicorn

app = FastAPI(title="Headwear Classifier API")

# Load model and labels
try:
    model = load_model("keras_model.h5", compile=False)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

try:
    with open("labels.txt", "r") as f:
        class_names = [line.strip()[2:] for line in f.readlines()]
except Exception as e:
    raise RuntimeError(f"Failed to load labels: {e}")

@app.post("/detect")
async def detect(image: UploadFile = File(...)):
    if not image.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Invalid image format. Use .jpg, .jpeg, or .png.")

    try:
        img = Image.open(image.file).convert("RGB")
        size = (224, 224)
        img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)

        image_array = np.asarray(img)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array

        prediction = model.predict(data)[0]
        top_index = np.argmax(prediction)
        top_label = class_names[top_index]
        confidence = float(prediction[top_index])

        return JSONResponse(content={
            "label": top_label,
            "confidence": round(confidence, 4)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# Uncomment below to run directly
# if __name__ == "__main__":
#     uvicorn.run("headwear_api:app", host="0.0.0.0", port=8000, reload=True)
