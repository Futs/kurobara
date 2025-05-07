from ..abstract_connector import Connector, ChapterData, SeriesData
import json
import re

class VizShonenJump(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.viz.com"
        self.api_url = "https://www.viz.com/shonenjump/chapters"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/shonenjump/chapters/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one("h2.type-center")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_element = document.select_one(".cover-image img")
        cover_url = cover_element.get("src") if cover_element else ""
        
        chapters = []
        chapter_elements = document.select(".chapter-list .o_chapter-container")
        
        for chapter_element in chapter_elements:
            link = chapter_element.select_one("a")
            if not link:
                continue
                
            href = link.get("href")
            chapter_id = href.split("/")[-1]
            name_element = chapter_element.select_one(".chapter-title")
            name = name_element.text.strip() if name_element else chapter_id
            
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
        chapter_url = f"{self.base_url}/shonenjump/{seriesId}/{chapterId}"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        # VIZ might load images via JavaScript and have DRM protections
        # Basic attempt to extract images - this might require more complex handling
        image_elements = document.select(".reader-image img")
        images = []
        
        for img in image_elements:
            src = img.get("data-src") or img.get("src")
            if src:
                images.append(src)
                
        # If no images found directly, try to find in JavaScript
        if not images:
            scripts = document.select("script")
            for script in scripts:
                if script.string and "mangaReaderPages" in script.string:
                    match = re.search(r'mangaReaderPages\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                    if match:
                        try:
                            pages_data = json.loads(match.group(1))
                            for page in pages_data:
                                if "image_url" in page:
                                    images.append(page["image_url"])
                        except json.JSONDecodeError:
                            pass
                
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }
