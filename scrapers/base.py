import aiohttp
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self):
        self.session = None

    async def fetch_json(self, url: str, params: dict = None):
        if not self.session:
            self.session = aiohttp.ClientSession()
        async with self.session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def close(self):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def scrape(self):
        pass