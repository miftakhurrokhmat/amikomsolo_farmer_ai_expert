# image_infer.py
# Sesuai training EfficientNetV2B0 (TF 2.19, Keras 3)
import os
import numpy as np
from PIL import Image
from keras.models import load_model
from keras.applications.efficientnet_v2 import preprocess_input as effnet_preprocess

# Lokasi model (ubah sesuai kebutuhan)
MODEL_PATH = os.getenv('MODEL_PATH', 'models/E6_efficient.keras')

# Load model sekali
try:
    model = load_model(MODEL_PATH, compile=False)
except Exception as e:
    model = None
    _load_error = str(e)
else:
    _load_error = None


def ensure_model_loaded():
    if model is None:
        raise RuntimeError(f"Model belum dimuat dari {MODEL_PATH}. Error: {_load_error}")


def preprocess_image(img_path, target_size=(224, 224)):
    """
    Preprocessing konsisten dengan training:
    - Resize ke (224,224)
    - RGB conversion
    - preprocess_input dari EfficientNetV2
    """
    img = Image.open(img_path).convert('RGB').resize(target_size)
    arr = np.asarray(img, dtype=np.float32)  # float32 (0..255)
    arr = effnet_preprocess(arr)  # sama dengan saat training
    arr = np.expand_dims(arr, axis=0)  # (1,224,224,3)
    return arr


def infer_image(img_path, top_k=1):
    """Prediksi gambar"""
    ensure_model_loaded()
    x = preprocess_image(img_path)
    preds = model.predict(x)
    preds = np.asarray(preds).reshape(-1)

    if preds.sum() == 0:
        probs = np.ones_like(preds) / preds.size
    else:
        probs = preds / preds.sum()

    if top_k == 1:
        idx = int(np.argmax(probs))
        conf = float(probs[idx])
        return idx, conf, probs.tolist()
    else:
        top_idx = np.argsort(probs)[::-1][:top_k]
        top_preds = [(int(i), float(probs[i])) for i in top_idx]
        return top_preds, probs.tolist()
