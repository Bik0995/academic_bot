import aiohttp
import re
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
        """Récupère le HTML d'une page avec le User‑Agent."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.HEADERS)
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def close(self):
        if self.session:
            await self.session.close()

    @staticmethod
    def extract_image_url(soup):
        """Cherche l'image principale d'un article (og:image, twitter:image, première image)."""
        if not soup:
            return None
        # og:image
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]
        # twitter:image
        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            return tw["content"]
        # Première image dans un article ou une div de contenu
        article = soup.find("article") or soup.find(class_=re.compile(r"post|entry"))
        if article:
            img = article.find("img")
            if img and img.get("src"):
                return img["src"]
        # Première image du document
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]
        return None

    @abstractmethod
    async def scrape(self):
        pass