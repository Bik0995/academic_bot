from telegram.ext import ApplicationBuilder, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TELEGRAM_BOT_TOKEN, CHANNEL_ID
from bot.handlers import start, latest, status
from models.database import engine
from models.opportunity import Base
from core.scheduler import scrape_and_publish

async def post_init(app):
    """Démarre le scheduler une fois la boucle d'événement initialisée."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scrape_and_publish,
        'interval',
        minutes=30,
        args=[app],
        id='scrape_job',
        replace_existing=True
    )
    scheduler.start()
    app.bot_data["scheduler"] = scheduler
    print("Scheduler démarré")

def main():
    # Création des tables de la base de données
    Base.metadata.create_all(bind=engine)

    # Application Telegram avec callback post_init
    app = ApplicationBuilder() \
        .token(TELEGRAM_BOT_TOKEN) \
        .post_init(post_init) \
        .build()
    app.bot_data["channel_id"] = CHANNEL_ID

    # Handlers des commandes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(CommandHandler("status", status))

    print("Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()