import hashlib
from bs4 import BeautifulSoup
from .base import BaseScraper
from core.cleaner import clean_html

class OpportunityDeskScraper(BaseScraper):
    BASE_URL = "https://opportunitydesk.org/"

    async def scrape(self):
        opportunities = []
        html = await self.fetch_html(self.BASE_URL)
        soup = BeautifulSoup(html, "html.parser")

        # Sélecteur très large : tout lien dans un titre (h2, h3) ou classe courante de WordPress
        title_links = soup.select("h2 a, h3 a, .entry-title a, .post-title a")
        print(f"OpportunityDesk : {len(title_links)} liens de titre trouvés")

        for link_el in title_links:
            title = link_el.get_text(strip=True)
            href = link_el.get("href")
            if not title or not href:
                continue

            # Récupération du résumé (dans l'élément parent le plus proche)
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
                "source": "OpportunityDesk",
                "hash": hash_val
            })

        print(f"OpportunityDesk : {len(opportunities)} offres construites")
        return opportunities