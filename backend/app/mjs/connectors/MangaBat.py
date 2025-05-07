from ..abstract_connector import Connector, ChapterData, SeriesData

class MangaBat(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://m.mangabat.com"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/manga/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one(".story-info-right h1")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_element = document.select_one(".info-image img")
        cover_url = cover_element.get("src") if cover_element else ""
        
        chapters = []
        chapter_elements = document.select(".row-content-chapter .a-h")
        
        for chapter_element in chapter_elements:
            link = chapter_element.select_one("a")
            if not link:
                continue
                
            href = link.get("href")
            # Extract the chapter ID from URL
            chapter_id = href.split("/")[-1].split("-")[-1]
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
        # Construct chapter URL based on ID pattern
        chapter_url = f"{self.base_url}/chapter/{seriesId}/chapter-{chapterId}"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        image_elements = document.select(".container-chapter-reader img")
        images = []
        
        for img in image_elements:
            src = img.get("src")
            if src:
                images.append(src)
                
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }
