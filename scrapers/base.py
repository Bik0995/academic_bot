import aiohttp
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
        """Nouvelle méthode pour récupérer du HTML avec User‑Agent."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.HEADERS)
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def close(self):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def scrape(self):
        pass