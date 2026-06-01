import hashlib
import xml.etree.ElementTree as ET
from .base import BaseScraper
from core.cleaner import clean_html

class DAADScraper(BaseScraper):
    RSS_URL = "https://www.daad.de/en/feed/"

    async def scrape(self):
        async with self.session.get(self.RSS_URL) as resp:
            resp.raise_for_status()
            text = await resp.text()

        opportunities = []
        root = ET.fromstring(text)
        items = root.findall(".//item")
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")

            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.text.strip() if link_el is not None and link_el.text else ""
            summary = clean_html(desc_el.text) if desc_el is not None and desc_el.text else ""

            if not title or not link:
                continue

            hash_val = hashlib.sha256(f"{title}{link}".encode()).hexdigest()
            opportunities.append({
                "title": title,
                "summary": summary,
                "country": "Germany",
                "level": "Various",
                "funding": "DAAD",
                "deadline": "Check site",
                "link": link,
                "source": "DAAD",
                "hash": hash_val
            })
        return opportunities