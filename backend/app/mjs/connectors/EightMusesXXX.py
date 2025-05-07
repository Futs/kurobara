from ..abstract_connector import Connector, ChapterData, SeriesData
import json
import re

class EightMusesXXX(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://comics.8muses.com"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/comics/album/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one(".top-menu-breadcrumb li:last-child")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_url = ""  # Default cover
        
        # Find album items
        album_items = document.select(".album-item")
        chapters = []
        
        for item in album_items:
            link = item.select_one("a")
            if not link:
                continue
                
            href = link.get("href")
            chapter_id = href.split("/")[-1]
            name_element = item.select_one(".album-name")
            name = name_element.text.strip() if name_element else chapter_id
            
            if not cover_url and item.select_one(".album-cover"):
                img = item.select_one(".album-cover img")
                if img:
                    cover_url = img.get("data-src") or img.get("src") or ""
                    
            chapters.append(ChapterData(
                id=chapter_id,
                name=name,
                series_id=seriesId
            ))
        
        return SeriesData(
            id=seriesId,
            title=title,
            cover_url=cover_url,
            chapters=chapters
        )
    
    async def get_chapter_data(self, seriesId, chapterId):
        chapter_url = f"{self.base_url}/comics/album/{chapterId}"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        images = []
        image_items = document.select(".image-item")
        
        for item in image_items:
            img = item.select_one("img")
            if img:
                src = img.get("data-src") or img.get("src")
                if src:
                    images.append(src)
                    
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }
