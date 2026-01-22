import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# --- DYNAMIC PATH SETUP ---
# This finds the 'medical-telegram-warehouse' folder automatically
BASE_DIR = Path(__file__).resolve().parent.parent 
JSON_BASE_PATH = BASE_DIR / "notebooks" / "data" / "raw" / "telegram_messages"
YOLO_CSV_PATH = BASE_DIR / "notebooks" / "data" / "raw" / "yolo_detections.csv"

DB_URL = "postgresql://postgres:1234@localhost:5432/medical_db"
engine = create_engine(DB_URL)

def load_json_to_postgres():
    """Traverses date folders and loads all JSON messages."""
    all_data = []

    print(f"Searching for JSON in: {JSON_BASE_PATH}")

    # 1. Iterate through date folders (e.g., 2026-01-19)
    if not JSON_BASE_PATH.exists():
        print(f"Error: Path {JSON_BASE_PATH} does not exist.")
        return

    for date_folder in JSON_BASE_PATH.iterdir():
        if date_folder.is_dir():
            # 2. Iterate through JSON files in each date folder
            for json_file in date_folder.glob("*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        all_data.extend(data)
                    except json.JSONDecodeError:
                        print(f"Skipping broken JSON: {json_file}")

    if not all_data:
        print("No Telegram JSON data found to load. Check your date folders.")
        return

    # 3. Convert to DataFrame
    df = pd.DataFrame(all_data)

    # 4. Handle Table Truncation and Loading
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()
        
        try:
            # Check if table exists by trying to truncate it
            conn.execute(text("TRUNCATE TABLE raw.telegram_messages;"))
            conn.commit()
            exists_action = "append"
            print("Table raw.telegram_messages truncated.")
        except Exception:
            # Table doesn't exist yet
            conn.rollback()
            exists_action = "replace"
            print("Table raw.telegram_messages does not exist. Creating new table.")

    df.to_sql(
        "telegram_messages",
        engine,
        schema="raw",
        if_exists=exists_action,
        index=False
    )
    print(f"Successfully loaded {len(df)} rows to raw.telegram_messages")

def load_yolo_to_postgres():
    """Loads YOLO results from CSV."""
    if not YOLO_CSV_PATH.exists():
        print(f"YOLO CSV not found at {YOLO_CSV_PATH}. Run src/yolo_detect.py first.")
        return

    df = pd.read_csv(YOLO_CSV_PATH)
    
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS detection;"))
        conn.commit()
    
    df.to_sql(
        "yolo_results", 
        engine, 
        schema="detection", 
        if_exists="replace", 
        index=False
    )
    print(f"Successfully loaded {len(df)} rows to detection.yolo_results")

if __name__ == "__main__":
    load_json_to_postgres()
    load_yolo_to_postgres()