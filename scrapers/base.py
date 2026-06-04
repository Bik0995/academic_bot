import aiohttp
import re
from urllib.parse import urljoin
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    def __init__(self):
        self.session = None

    async def fetch_json(self, url: str, params: dict = None):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.HEADERS)
        async with self.session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def fetch_html(self, url: str):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.HEADERS)
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def close(self):
        if self.session:
            await self.session.close()

    @staticmethod
    def extract_image_url_from_article(article_soup, base_url):
        if not article_soup:
            return None
        figure = article_soup.find("figure")
        if figure:
            img = figure.find("img")
            if img and img.get("src"):
                return urljoin(base_url, img["src"])
        for img in article_soup.find_all("img"):
            src = img.get("src")
            if src and not any(x in src.lower() for x in ["icon", "logo", "avatar", "gravatar", "flag"]):
                return urljoin(base_url, src)
        return None

    @staticmethod
    def extract_benefits(detail_soup):
        """Cherche une liste d'avantages uniquement dans une section 'Benefits' ou 'Scholarship covers'."""
        if not detail_soup:
            return []
        benefit_header = None
        for tag in detail_soup.find_all(['h2','h3','h4','strong','b']):
            txt = tag.get_text().lower()
            if ('benefits' in txt or 'scholarship covers' in txt) and 'eligibility' not in txt:
                benefit_header = tag
                break
        if not benefit_header:
            return []
        ul = benefit_header.find_next('ul') or benefit_header.find_next('ol')
        if not ul:
            return []
        items = []
        for li in ul.find_all('li'):
            txt = li.get_text(strip=True)
            if txt:
                items.append(txt)
        return items

    @staticmethod
    def extract_deadline(detail_soup):
        """Cherche une deadline uniquement si elle est annoncée par un mot-clé et pas trop ancienne."""
        if not detail_soup:
            return ""
        text = detail_soup.get_text(" ", strip=True)
        pattern = r"(?:deadline|apply\s*by|closing\s*date)[\s:]*([\w\s,]+?\d{4})"
        match = re.search(pattern, text, re.I)
        if match:
            candidate = match.group(1).strip()
            # Ignorer les dates avant 2025 (probablement une date de naissance ou autre)
            if re.search(r"\b(19\d{2}|20[01]\d|202[0-4])\b", candidate):
                return ""
            return candidate
        return ""

    @abstractmethod
    async def scrape(self):
        pass