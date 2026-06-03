import asyncio
from config import TELEGRAM_BOT_TOKEN, CHANNEL_ID
from models.database import engine
from models.opportunity import Base
from core.scheduler import scrape_and_publish

class FakeApp:
    """Simule l'application Telegram pour le publisher (juste besoin de bot et bot_data)."""
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
    # Crée les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)

    # Prépare une fausse application pour le publisher
    app = FakeApp(TELEGRAM_BOT_TOKEN, CHANNEL_ID)

    # Scrape et publie
    await scrape_and_publish(app)
    print("Exécution terminée.")

if __name__ == "__main__":
    asyncio.run(main())