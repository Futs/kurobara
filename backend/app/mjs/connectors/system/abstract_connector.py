from abc import ABC, abstractmethod
import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union

@dataclass
class ChapterData:
    id: str
    name: str
    series_id: str
    
@dataclass
class SeriesData:
    id: str
    title: str
    cover_url: str
    chapters: List[ChapterData]

class ConnectorErasureToken:
    """Token used to mark connectors for erasure in configuration"""
    pass

class Connector(ABC):
    def __init__(self):
        self.base_url = ""
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    async def fetch_document(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch HTML document from URL and parse with BeautifulSoup"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": self.user_agent}
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return None
                    html = await response.text()
                    return BeautifulSoup(html, "html.parser")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    @abstractmethod
    async def get_series_data(self, seriesId: str) -> Optional[SeriesData]:
        """Get series data including chapters list"""
        pass
    
    @abstractmethod
    async def get_chapter_data(self, seriesId: str, chapterId: str) -> Optional[Dict[str, Any]]:
        """Get chapter data including image URLs"""
        pass
