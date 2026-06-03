import asyncio
from scrapers.euraxess import EuraxessScraper
from scrapers.daad import DAADScraper
from scrapers.euroyouth import EuroYouthScraper
from scrapers.opportunitydesk import OpportunityDeskScraper
from scrapers.afterschoolafrica import AfterSchoolAfricaScraper
from scrapers.greatyop import GreatYopScraper
from scrapers.scholars4dev import Scholars4DevScraper
from scrapers.mladiinfo import MladiinfoScraper
from scrapers.youthop import YouthOpScraper
from scrapers.oyaop import OyaOpScraper
from scrapers.wemakescholars import WeMakeScholarsScraper
from core.deduplicator import process_opportunity
from bot.publisher import publish_opportunity

async def scrape_and_publish(app):
    scrapers = [
        EuraxessScraper(),
        DAADScraper(),
        EuroYouthScraper(),
        OpportunityDeskScraper(),
        AfterSchoolAfricaScraper(),
        GreatYopScraper(),
        Scholars4DevScraper(),
        MladiinfoScraper(),
        YouthOpScraper(),
        OyaOpScraper(),
        WeMakeScholarsScraper()
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