import asyncio
from scrapers.greatyop import GreatYopScraper
from scrapers.scholars4dev import Scholars4DevScraper
from scrapers.oyaop import OyaOpScraper
from core.deduplicator import process_opportunity
from bot.publisher import publish_opportunity

async def scrape_and_publish(app):
    scrapers = [
        GreatYopScraper(),
        Scholars4DevScraper(),
        OyaOpScraper()
    ]
    for scraper in scrapers:
        try:
            opportunities = await scraper.scrape()
            print(f"{scraper.__class__.__name__}: {len(opportunities)} offres trouvées")
            bot = app.bot
            channel_id = int(app.bot_data["channel_id"])
            for opp in opportunities:
                if process_opportunity(opp, opp["hash"]):
                    await publish_opportunity(bot, channel_id, opp)
                    # délai déjà inclus dans publish_opportunity
        except Exception as e:
            print(f"Erreur {scraper.__class__.__name__}: {e}")
        finally:
            await scraper.close()