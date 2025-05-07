from ..abstract_connector import Connector, ChapterData, SeriesData

class MangaTown(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.mangatown.com"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/manga/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        title_element = document.select_one("h1.title-top")
        if not title_element:
            return None
            
        title = title_element.text.strip()
        cover_element = document.select_one(".detail-info-cover img")
        cover_url = cover_element.get("src") if cover_element else ""
        
        chapters = []
        chapter_elements = document.select("#chapter_list li")
        
        for chapter_element in chapter_elements:
            link = chapter_element.select_one("a")
            if not link:
                continue
                
            href = link.get("href")
            chapter_id = href.split("/")[-1]
            name = link.select_one(".title").text.strip() if link.select_one(".title") else chapter_id
            
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
            
        image_elements = document.select(".read_img img")
        images = []
        
        # MangaTown usually displays one image at a time with page navigation
        # Need to handle pagination
        current_image = document.select_one(".read_img img")
        if current_image:
            src = current_image.get("src")
            if src:
                images.append(src)
                
        # Find total pages
        pages_element = document.select_one(".page_select select")
        if pages_element:
            page_options = pages_element.select("option")
            total_pages = len(page_options)
            
            # Extract current page number and base URL format
            if total_pages > 1 and current_image:
                current_url = chapter_url
                for page_num in range(1, total_pages + 1):
                    page_url = f"{chapter_url}/{page_num}.html"
                    if page_num == 1:
                        page_url = chapter_url
                        
                    # Load each page
                    page_document = await self.fetch_document(page_url)
                    if page_document:
                        page_img = page_document.select_one(".read_img img")
                        if page_img:
                            src = page_img.get("src")
                            if src and src not in images:
                                images.append(src)
                
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": images
        }
