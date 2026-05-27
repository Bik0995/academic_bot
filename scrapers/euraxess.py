import hashlib
from .base import BaseScraper
from core.cleaner import clean_html

class EuraxessScraper(BaseScraper):
    BASE_URL = "https://euraxess.ec.europa.eu/api/jobs"

    async def scrape(self):
        opportunities = []
        for page in range(1, 3):  # 2 pages
            params = {"page": page, "size": 20, "sort": "publicationDate,desc"}
            data = await self.fetch_json(self.BASE_URL, params=params)
            items = data.get("data", [])
            for item in items:
                opp = self._parse_item(item)
                if opp:
                    opportunities.append(opp)
        return opportunities

    def _parse_item(self, item: dict):
        try:
            title = item.get("title", "").strip()
            if not title:
                return None
            desc = item.get("description", "")
            summary = clean_html(desc) if desc else ""
            location = item.get("location", {})
            country = location.get("country", {}).get("name", "")
            job_types = item.get("jobType", [])
            level = ", ".join(jt.get("name", "") for jt in job_types) if job_types else ""
            salary = item.get("salary", "")
            funding = salary if salary else "Not specified"
            deadline = item.get("deadline", "Not specified")
            job_id = item.get("id")
            link = f"https://euraxess.ec.europa.eu/jobs/{job_id}" if job_id else ""
            if not link:
                return None
            hash_val = hashlib.sha256(f"{title}{link}".encode()).hexdigest()
            return {
                "title": title,
                "summary": summary,
                "country": country,
                "level": level,
                "funding": funding,
                "deadline": deadline,
                "link": link,
                "source": "EURAXESS",
                "hash": hash_val
            }
        except Exception:
            return None