import asyncio
from scrapers.euraxess import EuraxessScraper
from core.deduplicator import process_opportunity
from bot.publisher import publish_opportunity

async def scrape_and_publish(app):
    scraper = EuraxessScraper()
    try:
        opportunities = await scraper.scrape()
        bot = app.bot
        channel_id = int(app.bot_data["channel_id"])
        for opp in opportunities:
            if process_opportunity(opp, opp["hash"]):
                await publish_opportunity(bot, channel_id, opp)
                await asyncio.sleep(2)  # délai entre publications
    except Exception as e:
        print(f"Erreur scrape_and_publish : {e}")
    finally:
        await scraper.close()