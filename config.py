import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TELEGRAM_BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN et CHANNEL_ID sont requis")