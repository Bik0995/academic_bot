import aiohttp
import re
from urllib.parse import urljoin
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
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
    def extract_image_url(soup, base_url):
        """Cherche l'image principale et retourne l'URL absolue."""
        if not soup:
            return None
        candidates = [
            soup.find("meta", property="og:image"),
            soup.find("meta", attrs={"name": "twitter:image"}),
            soup.find("meta", property="twitter:image"),
        ]
        for meta in candidates:
            if meta and meta.get("content"):
                return urljoin(base_url, meta["content"])

        # Fallback : première image dans l'article
        article = soup.find("article") or soup.find(class_=re.compile(r"post|entry"))
        if article:
            img = article.find("img")
            if img and img.get("src"):
                return urljoin(base_url, img["src"])
        # Première image du document
        img = soup.find("img")
        if img and img.get("src"):
            return urljoin(base_url, img["src"])
        return None

    @abstractmethod
    async def scrape(self):
        pass