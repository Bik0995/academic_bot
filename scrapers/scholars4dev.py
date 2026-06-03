import hashlib
import re
from bs4 import BeautifulSoup
from .base import BaseScraper
from core.cleaner import clean_html

class Scholars4DevScraper(BaseScraper):
    BASE_URL = "https://www.scholars4dev.com/"

    async def scrape(self):
        opportunities = []
        html = await self.fetch_html(self.BASE_URL)
        soup = BeautifulSoup(html, "html.parser")

        articles = soup.select("article, .post, .entry")
        if not articles:
            title_links = soup.select("h2 a, h3 a, .entry-title a, .post-title a")
            articles = [link.find_parent(["article", "div.post", "div.entry"]) for link in title_links if link.find_parent(["article", "div.post", "div.entry"])]
        print(f"Scholars4Dev : {len(articles)} articles trouvés")

        for article in articles:
            title_el = article.select_one("h2 a, h3 a, .entry-title a, .post-title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href")
            if not title or not href:
                continue

            image_url = self.extract_image_url_from_article(article, self.BASE_URL)

            detail_soup = None
            try:
                detail_html = await self.fetch_html(href)
                detail_soup = BeautifulSoup(detail_html, "html.parser")
            except Exception as e:
                print(f"Erreur chargement détail {href}: {e}")

            summary = ""
            deadline = ""
            country = ""
            level = ""
            funding = ""
            if detail_soup:
                summary = self._extract_first(detail_soup, [".entry-content p", ".post-content p", "article p"])
                deadline = self._extract_first(detail_soup, [".deadline", ".application-deadline", "time", ".entry-date"])
                country = self._extract_first(detail_soup, [".country", ".location", ".entry-categories a", ".post-categories a"])
                level = self._extract_first(detail_soup, [".level", ".degree-level", ".eligibility"])
                funding = self._extract_first(detail_soup, [".funding", ".financial-aid", ".scholarship-type", ".benefits"])

            summary = clean_html(summary)[:300] if summary else ""
            deadline = deadline.strip() if deadline else ""
            country = country.strip() if country else ""
            level = level.strip() if level else ""
            funding = funding.strip() if funding else ""

            if not deadline and detail_soup:
                text = detail_soup.get_text()
                match = re.search(r"(?:deadline|apply by|closing date)[:\s]+([\w\s,0-9]+)", text, re.I)
                if match:
                    deadline = match.group(1).strip()

            hash_val = hashlib.sha256(f"{title}{href}".encode()).hexdigest()
            opportunities.append({
                "title": title,
                "summary": summary,
                "country": country,
                "level": level,
                "funding": funding,
                "deadline": deadline,
                "link": href,
                "source": "Scholars4Dev",
                "hash": hash_val,
                "image_url": image_url
            })

        print(f"Scholars4Dev : {len(opportunities)} offres construites")
        return opportunities

    def _extract_first(self, soup, selectors):
        if not soup:
            return ""
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                return el.get_text(strip=True)
        return ""