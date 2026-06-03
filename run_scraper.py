import asyncio
import sys
from config import TELEGRAM_BOT_TOKEN, CHANNEL_ID
from models.database import engine
from models.opportunity import Base
from core.scheduler import scrape_and_publish

class FakeApp:
    class FakeBot:
        def __init__(self, token):
            from telegram import Bot
            self._bot = Bot(token)
        async def send_message(self, *args, **kwargs):
            return await self._bot.send_message(*args, **kwargs)
    def __init__(self, token, channel_id):
        self.bot = self.FakeBot(token)
        self.bot_data = {"channel_id": channel_id}

async def main():
    Base.metadata.create_all(bind=engine)

    # Nettoyage et validation du channel_id
    raw = CHANNEL_ID.strip().strip('"').strip("'")
    if not raw.lstrip('-').isdigit():
        print(f"ERREUR : CHANNEL_ID invalide ({raw}). Vérifiez le secret GitHub.")
        sys.exit(1)
    
    app = FakeApp(TELEGRAM_BOT_TOKEN, raw)
    await scrape_and_publish(app)
    print("Exécution terminée.")

if __name__ == "__main__":
    asyncio.run(main())