import sys
import asyncio
from pathlib import Path
from dagster import op, job

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Now these imports will work!
from src.scraper import main as run_scraper 
from src.yolo_detect import run_detection
from src.to_postgres import load_json_to_postgres, load_yolo_to_postgres

@op
def scrape_op():
    # This runs your Telegram scraping code
    asyncio.run(run_scraper())
    return True

@op
def yolo_op(wait):
    # This runs your YOLO detection code
    run_detection()
    return True

@op
def load_op(wait):
    # This runs your Postgres loading code
    load_json_to_postgres()
    load_yolo_to_postgres()
    return True

@job
def telegram_medical_pipeline():
    s = scrape_op()
    y = yolo_op(s)
    l = load_op(y)