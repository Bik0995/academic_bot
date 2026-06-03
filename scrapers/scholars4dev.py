import hashlib
from bs4 import BeautifulSoup
from .base import BaseScraper
from core.cleaner import clean_html

class Scholars4DevScraper(BaseScraper):
    BASE_URL = "https://www.scholars4dev.com/"

    async def scrape(self):
        opportunities = []
        async with self.session.get(self.BASE_URL) as resp:
            html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article, .post, .entry")
        for article in articles:
            title_el = article.select_one("h2 a, h3 a, .entry-title a, .post-title a")
            if not title_el:
                continue
            title = title_el.text.strip()
            link = title_el.get("href")
            if not link:
                continue
            summary_el = article.select_one(".entry-summary, .post-content, .entry-content")
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
                "source": "Scholars4Dev",
                "hash": hash_val
            })
        print(f"Scholars4Dev : {len(opportunities)} offres extraites")
        return opportunities