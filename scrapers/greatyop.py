import hashlib
from bs4 import BeautifulSoup
from .base import BaseScraper
from core.cleaner import clean_html

class GreatYopScraper(BaseScraper):
    BASE_URL = "https://greatyop.com/"

    async def scrape(self):
        opportunities = []
        html = await self.fetch_html(self.BASE_URL)
        soup = BeautifulSoup(html, "html.parser")

        title_links = soup.select("h2 a, h3 a, .entry-title a, .post-title a")
        print(f"GreatYop : {len(title_links)} liens de titre trouvés")

        for link_el in title_links:
            title = link_el.get_text(strip=True)
            href = link_el.get("href")
            if not title or not href:
                continue

            parent_article = link_el.find_parent(["article", "div.post", "div.entry"])
            summary = ""
            if parent_article:
                summary_el = parent_article.select_one(".entry-summary, .post-content, .entry-content, p")
                if summary_el:
                    summary = clean_html(summary_el.get_text())

            hash_val = hashlib.sha256(f"{title}{href}".encode()).hexdigest()
            opportunities.append({
                "title": title,
                "summary": summary,
                "country": "",
                "level": "",
                "funding": "",
                "deadline": "",
                "link": href,
                "source": "GreatYop",
                "hash": hash_val
            })

        print(f"GreatYop : {len(opportunities)} offres construites")
        return opportunities