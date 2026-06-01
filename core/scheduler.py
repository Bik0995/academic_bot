import asyncio
from scrapers.euraxess import EuraxessScraper
from scrapers.daad import DAADScraper
from scrapers.euroyouth import EuroYouthScraper
from core.deduplicator import process_opportunity
from bot.publisher import publish_opportunity

async def scrape_and_publish(app):
    scrapers = [
        EuraxessScraper(),
        DAADScraper(),
        EuroYouthScraper()
    ]
    for scraper in scrapers:
        try:
            opportunities = await scraper.scrape()
            bot = app.bot
            channel_id = int(app.bot_data["channel_id"])
            for opp in opportunities:
                if process_opportunity(opp, opp["hash"]):
                    await publish_opportunity(bot, channel_id, opp)
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"Erreur {scraper.__class__.__name__}: {e}")
        finally:
            await scraper.close()