from ..abstract_connector import Connector, ChapterData, SeriesData, ConnectorErasureToken

class AniGliScans(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://anigliscans.xyz"
        self.base_reader_url = f"{self.base_url}/series"
        self.dummy_image_url = f"{self.base_url}/dummy_image.jpg"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_reader_url}/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title = document.select_one(".series-title")
        if not title:
            return None
            
        title_text = title.text.strip()
        cover_img = document.select_one(".thumb img")
        cover_url = cover_img.get("src") if cover_img else self.dummy_image_url
        
        chapters = []
        chapter_elements = document.select(".wp-manga-chapter")
        
        for chapter_element in chapter_elements:
            link = chapter_element.select_one("a")
            if not link:
                continue
                
            chapter_id = link.get("href").split("/")[-2]
            chapter_name = link.text.strip()
            
            chapters.append(ChapterData(
                id=chapter_id,
                name=chapter_name,
                series_id=seriesId
            ))
            
        return SeriesData(
            id=seriesId,
            title=title_text,
            cover_url=cover_url,
            chapters=chapters
        )
    
    async def get_chapter_data(self, seriesId, chapterId):
        chapter_url = f"{self.base_reader_url}/{seriesId}/{chapterId}"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        image_elements = document.select(".reading-content img")
        images = []
        
        for img in image_elements:
            src = img.get("src") or img.get("data-src")
            if src:
                images.append(src)
                
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }
