# ai_module.py
import os, json
from image_infer import infer_image

# Load database penyakit
DB_PATH = os.path.join(os.path.dirname(__file__), 'diseases.json')
try:
    with open(DB_PATH, 'r', encoding='utf-8') as fh:
        DISEASE_DB = json.load(fh).get("diseases", {})
except Exception:
    DISEASE_DB = {}

# Label model = key JSON
LABELS = list(DISEASE_DB.keys()) if DISEASE_DB else [
    "Bacterial_Blight_Disease",
    "Blast_Disease",
    "Brown_Spot_Disease",
    "False_Smut_Disease",
    "Healthy_Rice_Leaf",
    "Narrow_Brown_Spot",
    "Sheath_Blight_Disease",
    "Tungro_Virus",    
]


def find_details(label):
    """Cari detail penyakit berdasarkan label atau alias"""
    if label in DISEASE_DB:
        return DISEASE_DB[label]
    for k, v in DISEASE_DB.items():
        if "alias" in v and label in v["alias"]:
            return v
    return {
        "nama_penyakit": label,
        "alias": [],
        "nama_latin": None,
        "gejala": "-",
        "rekomendasi": "Tidak ada data"
    }


def analyze(image_path, top_k=1):
    result = infer_image(image_path, top_k=top_k)

    if top_k == 1:
        idx, conf, raw = result
        label = LABELS[idx] if idx < len(LABELS) else f"class_{idx}"
        details = find_details(label)
        return {
            "label_index": idx,
            "label": label,
            "confidence": round(conf, 4),
            "details": details,
            "raw_scores": raw
        }
    else:
        top_preds, raw = result
        candidates = []
        for idx, conf in top_preds:
            label = LABELS[idx] if idx < len(LABELS) else f"class_{idx}"
            details = find_details(label)
            candidates.append({
                "label_index": idx,
                "label": label,
                "confidence": round(conf, 4),
                "details": details
            })
        return {
            "top_predictions": candidates,
            "raw_scores": raw
        }
