import hashlib
import re
from bs4 import BeautifulSoup
from .base import BaseScraper
from core.cleaner import clean_html

class GreatYopScraper(BaseScraper):
    BASE_URL = "https://greatyop.com/"
    DETAIL_SELECTORS = {
        "summary": [".entry-content p", ".post-content p", "article p"],
        "deadline": [".deadline", ".application-deadline", "time", ".entry-date"],
        "country": [".country", ".location", ".entry-categories a", ".post-categories a"],
        "level": [".level", ".degree-level", ".eligibility"],
        "funding": [".funding", ".financial-aid", ".scholarship-type", ".benefits"]
    }

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

            detail_soup = None
            try:
                detail_html = await self.fetch_html(href)
                detail_soup = BeautifulSoup(detail_html, "html.parser")
            except Exception:
                pass

            summary = self._extract_first(detail_soup, self.DETAIL_SELECTORS["summary"])
            deadline = self._extract_first(detail_soup, self.DETAIL_SELECTORS["deadline"])
            country = self._extract_first(detail_soup, self.DETAIL_SELECTORS["country"])
            level = self._extract_first(detail_soup, self.DETAIL_SELECTORS["level"])
            funding = self._extract_first(detail_soup, self.DETAIL_SELECTORS["funding"])

            summary = clean_html(summary)[:280] if summary else ""
            deadline = deadline.strip() if deadline else ""
            country = country.strip() if country else ""
            level = level.strip() if level else ""
            funding = funding.strip() if funding else ""

            if not deadline and detail_soup:
                text = detail_soup.get_text()
                match = re.search(r"(?:deadline|apply by|closing date)[:\s]+([\w\s,]+)", text, re.I)
                if match:
                    deadline = match.group(1).strip()

            image_url = self.extract_image_url(detail_soup)

            hash_val = hashlib.sha256(f"{title}{href}".encode()).hexdigest()
            opportunities.append({
                "title": title,
                "summary": summary,
                "country": country,
                "level": level,
                "funding": funding,
                "deadline": deadline,
                "link": href,
                "source": "GreatYop",
                "hash": hash_val,
                "image_url": image_url
            })

        print(f"GreatYop : {len(opportunities)} offres construites")
        return opportunities

    def _extract_first(self, soup, selectors):
        if not soup:
            return ""
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                return el.get_text(strip=True)
        return ""