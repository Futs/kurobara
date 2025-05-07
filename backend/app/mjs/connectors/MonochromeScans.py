from ..abstract_connector import Connector, ChapterData, SeriesData

class MonochromeScans(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://monochromescans.com"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/comics/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one(".comic-info h1.comic-title")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_element = document.select_one(".comic-image img")
        cover_url = cover_element.get("src") if cover_element else ""
        
        chapters = []
        chapter_elements = document.select(".chapters-list .chapter-item")
        
        for chapter_element in chapter_elements:
            link = chapter_element.select_one("a")
            if not link:
                continue
                
            href = link.get("href")
            chapter_id = href.split("/")[-1]
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
        chapter_url = f"{self.base_url}/reader/{chapterId}"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        image_elements = document.select(".viewer-container img.page")
        images = []
        
        for img in image_elements:
            src = img.get("data-src") or img.get("src")
            if src:
                images.append(src)
                
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }