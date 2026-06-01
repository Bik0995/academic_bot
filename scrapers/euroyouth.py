import hashlib
from .base import BaseScraper

class EuroYouthScraper(BaseScraper):
    API_URL = "https://youth.europa.eu/api/opportunities"

    async def scrape(self):
        opportunities = []
        for opp_type in ["scholarship", "internship", "training"]:
            params = {"type": opp_type, "limit": 20}
            try:
                data = await self.fetch_json(self.API_URL, params=params)
                items = data.get("data", [])
                for item in items:
                    title = item.get("title", "").strip()
                    link = item.get("url", "")
                    if not title or not link:
                        continue
                    summary = item.get("description", "")[:280]
                    country = item.get("country", {}).get("name", "")
                    deadline = item.get("deadline", "Check site")
                    hash_val = hashlib.sha256(f"{title}{link}".encode()).hexdigest()
                    opportunities.append({
                        "title": title,
                        "summary": summary,
                        "country": country,
                        "level": item.get("level", "Various"),
                        "funding": item.get("funding", "Not specified"),
                        "deadline": deadline,
                        "link": link,
                        "source": "EuropeanYouthPortal",
                        "hash": hash_val
                    })
            except Exception as e:
                print(f"EuroYouth scraper error ({opp_type}): {e}")
        return opportunities