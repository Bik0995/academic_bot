import asyncio
from scrapers.opportunitydesk import OpportunityDeskScraper   # à réactiver plus tard
from scrapers.afterschoolafrica import AfterSchoolAfricaScraper # idem
from scrapers.greatyop import GreatYopScraper
from scrapers.scholars4dev import Scholars4DevScraper
from scrapers.mladiinfo import MladiinfoScraper
from scrapers.youthop import YouthOpScraper
from scrapers.oyaop import OyaOpScraper
from scrapers.wemakescholars import WeMakeScholarsScraper
from core.deduplicator import process_opportunity
from bot.publisher import publish_opportunity

async def scrape_and_publish(app):
    # Ne garder que les scrapers qui fonctionnent actuellement
    scrapers = [
        # OpportunityDeskScraper(),   # 403
        # AfterSchoolAfricaScraper(), # 403
        GreatYopScraper(),
        Scholars4DevScraper(),
        # MladiinfoScraper(),         # 0 offres
        # YouthOpScraper(),           # 0 offres
        OyaOpScraper(),
        # WeMakeScholarsScraper(),    # 0 offres
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
                    await asyncio.sleep(3)   # délai plus long pour éviter le flood
        except Exception as e:
            print(f"Erreur {scraper.__class__.__name__}: {e}")
        finally:
            await scraper.close()