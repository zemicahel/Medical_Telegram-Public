import os
import pandas as pd
from pathlib import Path
from ultralytics import YOLO
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- DYNAMIC PATH SETUP ---
# Finds the root 'medical-telegram-warehouse' folder
BASE_DIR = Path(__file__).resolve().parent.parent 
IMAGE_DIR = BASE_DIR / "notebooks" / "data" / "raw" / "images"
OUTPUT_CSV = BASE_DIR / "notebooks" / "data" / "raw" / "yolo_detections.csv"

# Load pre-trained YOLOv8n model
# It will automatically download 'yolov8n.pt' the first time you run it
model = YOLO('yolov8n.pt') 

def classify_image(detected_objects):
    """
    Classification Scheme:
    - promotional: Person + Product (bottle, cup, bowl, vase, etc.)
    - product_display: Product only, no Person
    - lifestyle: Person only, no Product
    - other: Neither detected
    """
    has_person = 'person' in detected_objects
    # Common YOLO classes that represent medical/cosmetic packaging
    container_classes = {'bottle', 'cup', 'bowl', 'vase', 'toothbrush'}
    has_product = any(obj in container_classes for obj in detected_objects)

    if has_person and has_product:
        return 'promotional'
    elif has_product and not has_person:
        return 'product_display'
    elif has_person and not has_product:
        return 'lifestyle'
    else:
        return 'other'

def run_detection():
    results_list = []

    if not IMAGE_DIR.exists():
        logger.error(f"Image directory not found at: {IMAGE_DIR}")
        return

    # Iterate through channel folders (e.g., lobelia4cosmetics, tikvahpharma)
    for channel_path in IMAGE_DIR.iterdir():
        if channel_path.is_dir():
            channel_name = channel_path.name
            logger.info(f"🔍 Processing images for channel: {channel_name}")

            for img_file in channel_path.glob("*.jpg"):
                msg_id = img_file.stem
                
                # Run YOLO detection
                results = model(img_file, conf=0.25, verbose=False)
                
                detected_names = []
                confidences = []
                
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        name = model.names[cls_id]
                        conf = float(box.conf[0])
                        detected_names.append(name)
                        confidences.append(conf)

                # Apply classification based on the list of objects found
                category = classify_image(detected_names)

                results_list.append({
                    "message_id": msg_id,
                    "channel": channel_name,
                    "detected_objects": ",".join(detected_names) if detected_names else "none",
                    "confidence_scores": ",".join([f"{c:.2f}" for c in confidences]) if confidences else "0.00",
                    "image_category": category
                })

    # Save to CSV in the data folder
    if results_list:
        df = pd.DataFrame(results_list)
        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"✅ Detection complete. Results saved to {OUTPUT_CSV}")
    else:
        logger.warning("No images were found to process.")

if __name__ == "__main__":
    run_detection()