import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import logging
from urllib.parse import urljoin
import json

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.results = []

    async def __aenter__(self):
        headers = self.config.get("headers", {})
        if not headers.get("User-Agent"):
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate(self) -> bool:
        """Handle authentication if required"""
        auth_config = self.config.get("authentication")
        if not auth_config:
            return True

        auth_url = auth_config.get("url")
        auth_data = auth_config.get("data", {})
        
        try:
            async with self.session.post(auth_url, json=auth_data) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    if auth_response.get("token"):
                        self.session.headers.update({
                            "Authorization": f"Bearer {auth_response['token']}"
                        })
                    return True
                return False
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    async def extract_data(self, html: str, url: str) -> Dict[str, Any]:
        """Extract data from HTML using configured selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        
        for field, selector in self.config["selectors"].items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    data[field] = elements[0].get_text(strip=True)
                else:
                    data[field] = [el.get_text(strip=True) for el in elements]
            else:
                data[field] = None
        
        data["source_url"] = url
        return data

    def apply_filters(self, data: Dict[str, Any]) -> bool:
        """Apply configured filters to scraped data"""
        filters = self.config.get("filters", {})
        if not filters:
            return True

        for field, conditions in filters.items():
            value = data.get(field)
            if not value:
                continue

            for condition, expected in conditions.items():
                if condition == "contains" and expected.lower() not in value.lower():
                    return False
                elif condition == "equals" and value.lower() != expected.lower():
                    return False
                elif condition == "startswith" and not value.lower().startswith(expected.lower()):
                    return False
                elif condition == "endswith" and not value.lower().endswith(expected.lower()):
                    return False

        return True

    async def get_next_page_url(self, html: str, current_url: str) -> str | None:
        """Get next page URL using pagination configuration"""
        pagination = self.config.get("pagination")
        if not pagination:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        next_link = soup.select_one(pagination["next_page_selector"])
        
        if next_link and next_link.get("href"):
            return urljoin(current_url, next_link["href"])
        return None

    async def scrape_page(self, url: str) -> List[Dict[str, Any]]:
        """Scrape a single page"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: {response.status}")
                    return []

                html = await response.text()
                data = await self.extract_data(html, url)
                
                if self.apply_filters(data):
                    self.results.append(data)
                
                return await self.get_next_page_url(html, url)
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    async def run(self) -> List[Dict[str, Any]]:
        """Run the scraper"""
        try:
            if not await self.authenticate():
                raise Exception("Authentication failed")

            url = self.config["url_pattern"]
            while url:
                next_url = await self.scrape_page(url)
                if not next_url:
                    break
                url = next_url

            return self.results
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            raise
