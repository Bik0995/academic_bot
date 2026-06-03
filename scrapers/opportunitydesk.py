import hashlib
from bs4 import BeautifulSoup
from .base import BaseScraper
from core.cleaner import clean_html

class OpportunityDeskScraper(BaseScraper):
    BASE_URL = "https://opportunitydesk.org/"

    async def scrape(self):
        opportunities = []
        async with self.session.get(self.BASE_URL) as resp:
            html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article")
        for article in articles:
            title_el = article.select_one("h2 a, .entry-title a")
            if not title_el:
                continue
            title = title_el.text.strip()
            link = title_el.get("href")
            if not link:
                continue
            summary_el = article.select_one(".entry-summary, .post-content")
            summary = clean_html(summary_el.text) if summary_el else ""
            hash_val = hashlib.sha256(f"{title}{link}".encode()).hexdigest()
            opportunities.append({
                "title": title,
                "summary": summary,
                "country": "",
                "level": "",
                "funding": "",
                "deadline": "",
                "link": link,
                "source": "OpportunityDesk",
                "hash": hash_val
            })
        return opportunities