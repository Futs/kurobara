from ..abstract_connector import Connector, ChapterData, SeriesData
import re
import json

class IMHentai(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://imhentai.xxx"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/gallery/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one("h1")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_element = document.select_one(".cover img")
        cover_url = cover_element.get("data-src") or cover_element.get("src") if cover_element else ""
        
        # For galleries like IMHentai, typically there's only one "chapter" which is the gallery itself
        chapters = [
            ChapterData(
                id=seriesId,
                name="Gallery",
                series_id=seriesId
            )
        ]
        
        return SeriesData(
            id=seriesId,
            title=title,
            cover_url=cover_url,
            chapters=chapters
        )
    
    async def get_chapter_data(self, seriesId, chapterId):
        gallery_url = f"{self.base_url}/gallery/{seriesId}/1"
        document = await self.fetch_document(gallery_url)
        
        if not document:
            return None
        
        # Try to find the reader script which contains image data
        scripts = document.select("script")
        image_data = []
        total_pages = 0
        
        for script in scripts:
            if script.string and "var g_th" in script.string:
                # Extract pages count
                pages_match = re.search(r'var g_num_pages\s*=\s*(\d+)', script.string)
                if pages_match:
                    total_pages = int(pages_match.group(1))
                
        server_url = ""
        server_match = re.search(r'var g_server\s*=\s*"([^"]+)"', script.string) if script.string else None
        if server_match:
            server_url = server_match.group(1)
            
        images = []
        if total_pages and server_url:
            for i in range(1, total_pages + 1):
                image_url = f"{server_url}/gallery/{seriesId}/{i}.jpg"
                images.append(image_url)
                
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }
