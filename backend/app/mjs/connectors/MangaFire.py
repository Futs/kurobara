from ..abstract_connector import Connector, ChapterData, SeriesData
import json
import re

class MangaFire(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://mangafire.to"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/manga/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one("h1.manga-name")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_element = document.select_one(".manga-poster img")
        cover_url = cover_element.get("src") if cover_element else ""
        
        chapters = []
        chapter_elements = document.select(".chapter-item")
        
        for chapter_element in chapter_elements:
            link = chapter_element.select_one("a")
            if not link:
                continue
                
            href = link.get("href")
            chapter_id = href.split("/")[-1]
            name_element = chapter_element.select_one(".chapter-name")
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
        chapter_url = f"{self.base_url}/read/{seriesId}/{chapterId}"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        # MangaFire often loads images via JavaScript, we need to extract the data
        scripts = document.select("script")
        images = []
        
        for script in scripts:
            if script.string and "chapImages" in script.string:
                # Extract image data from script
                match = re.search(r'chapImages\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if match:
                    try:
                        image_data = json.loads(match.group(1))
                        for img in image_data:
                            if isinstance(img, str):
                                images.append(img)
                            elif isinstance(img, dict) and "src" in img:
                                images.append(img["src"])
                    except json.JSONDecodeError:
                        pass
                        
        # If no images found through script, try direct DOM access
        if not images:
            image_elements = document.select(".chapter-img")
            for img in image_elements:
                src = img.get("data-src") or img.get("src")
                if src:
                    images.append(src)
                    
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }
