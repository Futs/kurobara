from ..abstract_connector import Connector, ChapterData, SeriesData

class ManhuaUs(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://manhuaus.com"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/manga/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one(".post-title h1")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_element = document.select_one(".summary_image img")
        cover_url = cover_element.get("data-src") or cover_element.get("src") if cover_element else ""
        
        chapters = []
        chapter_elements = document.select("li.wp-manga-chapter")
        
        for chapter_element in chapter_elements:
            link = chapter_element.select_one("a")
            if not link:
                continue
                
            href = link.get("href")
            chapter_id = href.split("/")[-2]
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
        chapter_url = f"{self.base_url}/manga/{seriesId}/{chapterId}"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        image_elements = document.select(".reading-content img")
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
