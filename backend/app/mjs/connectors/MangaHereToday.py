from ..abstract_connector import Connector, ChapterData, SeriesData
import re
import json

class MangaHereToday(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.mangahere.today"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/manga/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one(".manga-info h1")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_element = document.select_one(".manga-info-pic img")
        cover_url = cover_element.get("src") if cover_element else ""
        
        chapters = []
        chapter_elements = document.select(".chapter-list .row")
        
        for chapter_element in chapter_elements:
            link = chapter_element.select_one("a")
            if not link:
                continue
                
            href = link.get("href")
            chapter_id = href.split("/")[-1].replace(".html", "")
            name = link.text.strip()
            
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
        chapter_url = f"{self.base_url}/manga/{seriesId}/{chapterId}.html"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        # MangaHereToday often loads images via JavaScript
        images = []
        scripts = document.select("script")
        
        for script in scripts:
            script_text = script.string if script.string else ""
            if "var images" in script_text:
                # Try to extract the image array
                match = re.search(r'var\s+images\s*=\s*(\[.*?\]);', script_text, re.DOTALL)
                if match:
                    try:
                        image_data = json.loads(match.group(1))
                        images = image_data
                    except json.JSONDecodeError:
                        pass
        
        # If JavaScript extraction fails, try direct image extraction
        if not images:
            image_elements = document.select(".reader-content img")
            for img in image_elements:
                src = img.get("src") or img.get("data-src")
                if src:
                    images.append(src)
                    
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }
