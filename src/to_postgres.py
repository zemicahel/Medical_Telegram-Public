import os
import json
import pandas as pd
from sqlalchemy import create_engine, text  # Import 'text'
from pathlib import Path

DB_URL = "postgresql://postgres:1234@localhost:5432/medical_db"
engine = create_engine(DB_URL)

JSON_BASE_PATH = Path("data/raw/telegram_messages")

def load_json_to_postgres():
    all_data = []

    # 1. Collection logic
    for date_folder in JSON_BASE_PATH.iterdir():
        if date_folder.is_dir():
            for json_file in date_folder.glob("*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)

    if not all_data:
        print("No data found to load.")
        return

    # 2. Convert to DataFrame
    df = pd.DataFrame(all_data)

    # 3. Create Schema and Load Data
    with engine.connect() as conn:
        # Wrap the string in text() and commit the transaction
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit() 

    # Pandas to_sql handles its own connection, so we use the engine directly here
    df.to_sql(
        "telegram_messages",
        engine,
        schema="raw",
        if_exists="replace",
        index=False
    )

    print(f"Successfully loaded {len(df)} rows to raw.telegram_messages")