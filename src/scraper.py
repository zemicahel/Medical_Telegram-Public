import os
import json
import logging
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient, errors

nest_asyncio.apply()
load_dotenv()

# Configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
CHANNELS = [
    'https://t.me/lobelia4cosmetics',
    'https://t.me/tikvahpharma',
    'chemedtelegram',
]

# Path Setup - Use absolute paths based on project root
BASE_DIR = Path(__file__).resolve().parent.parent
# We use the 'notebooks/data' path you mentioned earlier
IMAGE_BASE_PATH = BASE_DIR / "notebooks" / "data" / "raw" / "images"
JSON_BASE_PATH = BASE_DIR / "notebooks" / "data" / "raw" / "telegram_messages"
LOG_PATH = BASE_DIR / "logs"

for path in [IMAGE_BASE_PATH, JSON_BASE_PATH, LOG_PATH]:
    path.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH / "scraping.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def scrape_channel(client, channel_username):
    """Scrapes messages and images from a single channel."""
    try:
        entity = await client.get_entity(channel_username)
        channel_name = entity.username or entity.title
        logger.info(f"Starting scrape for: {channel_name}")

        messages_data = []
        async for message in client.iter_messages(entity, limit=50):
            image_path = None
            if message.photo:
                image_folder = IMAGE_BASE_PATH / channel_name
                image_folder.mkdir(parents=True, exist_ok=True)
                file_name = f"{message.id}.jpg"
                save_path = image_folder / file_name
                image_path = await client.download_media(message.photo, file=str(save_path))

            messages_data.append({
                "message_id": message.id,
                "date": message.date.isoformat(),
                "text": message.text,
                "views": message.views,
                "forwards": message.forwards,
                "image_path": str(image_path) if image_path else None,
                "channel": channel_name
            })

        today_str = datetime.now().strftime("%Y-%m-%d")
        partition_path = JSON_BASE_PATH / today_str
        partition_path.mkdir(parents=True, exist_ok=True)
        
        json_file = partition_path / f"{channel_name}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Successfully saved {len(messages_data)} messages for {channel_name}")

    except Exception as e:
        logger.error(f"Error scraping {channel_username}: {str(e)}")

async def main():
    """This is the entry point that Dagster will call."""
    # The session file will be stored in the root folder
    session_file = str(BASE_DIR / "scraper_session")
    async with TelegramClient(session_file, API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)

if __name__ == "__main__":
    asyncio.run(main())