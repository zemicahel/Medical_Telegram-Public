from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .database import get_db
from . import schemas

app = FastAPI(
    title="Medical Telegram Analytics API",
    description="API for accessing Ethiopian medical business data and AI insights",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Telegram Analytics API. Visit /docs for documentation."}

# Endpoint 1: Top Products (Frequently mentioned terms)
@app.get("/api/reports/top-products", response_model=List[schemas.ProductCount])
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    query = text("""
        SELECT word as term, count(*) as count
        FROM (
            SELECT regexp_split_to_table(lower(message_text), '\s+') as word
            FROM fct_messages
        ) t
        WHERE length(word) > 4  -- Filter out small common words
        GROUP BY word
        ORDER BY count DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit}).fetchall()
    return result

# Endpoint 2: Channel Activity
@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT TO_CHAR(full_date, 'YYYY-MM-DD') as date, count(m.message_id) as message_count
        FROM dim_dates d
        LEFT JOIN fct_messages m ON d.date_key = m.date_key
        JOIN dim_channels c ON m.channel_key = c.channel_key
        WHERE c.channel_name = :channel_name
        GROUP BY full_date
        ORDER BY full_date DESC
    """)
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Channel not found or no activity")
    return result

# Endpoint 3: Message Search
@app.get("/api/search/messages", response_model=List[schemas.MessageResponse])
def search_messages(query: str, limit: int = 20, db: Session = Depends(get_db)):
    sql_query = text("""
        SELECT m.message_id, c.channel_name, m.message_text as text, 
               m.view_count, d.full_date as message_date
        FROM fct_messages m
        JOIN dim_channels c ON m.channel_key = c.channel_key
        JOIN dim_dates d ON m.date_key = d.date_key
        WHERE m.message_text ILIKE :search_query
        LIMIT :limit
    """)
    result = db.execute(sql_query, {"search_query": f"%{query}%", "limit": limit}).fetchall()
    return result

# Endpoint 4: Visual Content Stats (Uses Task 3's logic)
@app.get("/api/reports/visual-content", response_model=List[schemas.VisualContentStats])
def get_visual_stats(db: Session = Depends(get_db)):
    # Note: Ensure you have run Task 3 and the fct_image_detections exists
    query = text("""
        SELECT c.channel_name, i.image_category, count(*) as count
        FROM fct_image_detections i
        JOIN dim_channels c ON i.channel_key = c.channel_key
        GROUP BY c.channel_name, i.image_category
        ORDER BY c.channel_name, count DESC
    """)
    result = db.execute(query).fetchall()
    return result