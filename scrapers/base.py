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
        """Extrait l'URL absolue de la miniature d'un article (page liste)."""
        if not article_soup:
            return None
        # Cherche dans l'ordre : figure, img sans classe d'icône
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
        """Cherche une liste d'avantages (li) dans une section contenant 'benefit'."""
        if not detail_soup:
            return []
        # Chercher un élément dont le texte contient "benefit" (h2, h3, strong)
        benefit_header = None
        for tag in detail_soup.find_all(['h2','h3','h4','strong','b']):
            if 'benefit' in tag.get_text().lower():
                benefit_header = tag
                break
        if not benefit_header:
            # Fallback : cherche n'importe quelle liste après le premier paragraphe
            benefit_header = detail_soup.find('p')
        if not benefit_header:
            return []
        # Récupère la liste suivant immédiatement ce titre (ul/ol)
        ul = benefit_header.find_next('ul') or benefit_header.find_next('ol')
        if not ul:
            # Parfois les avantages sont dans des div ou p, on ne peut pas tout deviner
            return []
        items = []
        for li in ul.find_all('li'):
            txt = li.get_text(strip=True)
            if txt:
                items.append(txt)
        return items

    @abstractmethod
    async def scrape(self):
        pass