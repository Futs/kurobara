from ..abstract_connector import Connector, ChapterData, SeriesData
import json
import re

class MangaLife(Connector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://manga4life.com"
        
    async def get_series_data(self, seriesId):
        series_url = f"{self.base_url}/manga/{seriesId}"
        document = await self.fetch_document(series_url)
        
        if not document:
            return None
            
        # MangaLife loads data via JavaScript, so we need to extract from scripts
        scripts = document.select("script")
        series_data = None
        chapters_data = None
        
        for script in scripts:
            if script.string and "vm.SeriesName" in script.string:
                # Extract series title
                title_match = re.search(r'vm\.SeriesName\s*=\s*"([^"]+)"', script.string)
                if title_match:
                    series_title = title_match.group(1)
                
                # Extract cover URL
                cover_match = re.search(r'vm\.SeriesImage\s*=\s*"([^"]+)"', script.string)
                cover_url = ""
                if cover_match:
                    cover_path = cover_match.group(1)
                    cover_url = f"{self.base_url}/cover/{cover_path}"
                
                # Extract chapters
                chapters_match = re.search(r'vm\.Chapters\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if chapters_match:
                    try:
                        chapters_data = json.loads(chapters_match.group(1))
                    except json.JSONDecodeError:
                        chapters_data = []
        
        if not series_title:
            # Try to get title from DOM if script extraction failed
            title_element = document.select_one("h1")
            if title_element:
                series_title = title_element.text.strip()
            else:
                return None
                
        chapters = []
        if chapters_data:
            for chapter in chapters_data:
                chapter_num = chapter.get("Chapter", "")
                # MangaLife uses a specific format for chapter IDs
                # Convert to readable format (e.g., "100005" → "1.5")
                chapter_num_int = int(chapter_num[1:-1])
                chapter_decimal = chapter_num[-1]
                
                formatted_ch = str(chapter_num_int)
                if chapter_decimal != "0":
                    formatted_ch = f"{formatted_ch}.{chapter_decimal}"
                    
                chapter_name = f"Chapter {formatted_ch}"
                if chapter.get("ChapterName"):
                    chapter_name += f": {chapter.get('ChapterName')}"
                    
                chapters.append(ChapterData(
                    id=chapter_num,
                    name=chapter_name,
                    series_id=seriesId
                ))
        
        return SeriesData(
            id=seriesId,
            title=series_title,
            cover_url=cover_url,
            chapters=chapters
        )
    
    async def get_chapter_data(self, seriesId, chapterId):
        # MangaLife has a specific URL format for chapters
        chapter_num_int = int(chapterId[1:-1])
        chapter_decimal = chapterId[-1]
        
        formatted_ch = str(chapter_num_int)
        if chapter_decimal != "0":
            formatted_ch = f"{formatted_ch}.{chapter_decimal}"
            
        chapter_url = f"{self.base_url}/read-online/{seriesId}/chapter-{formatted_ch}"
        document = await self.fetch_document(chapter_url)
        
        if not document:
            return None
            
        # The images are loaded via JavaScript
        scripts = document.select("script")
        image_array = None
        
        for script in scripts:
            if script.string and "vm.CurChapter" in script.string:
                # Extract image data
                match = re.search(r'vm\.CurPathName\s*=\s*"([^"]+)"', script.string)
                if match:
                    path_name = match.group(1)
                    
                directory_match = re.search(r'vm\.CurChapter\s*=\s*(\{.*?\});', script.string, re.DOTALL)
                if directory_match:
                    try:
                        chapter_info = json.loads(directory_match.group(1))
                        directory = chapter_info.get("Directory", "")
                        
                        # Extract number of pages
                        pages_match = re.search(r'vm\.PageArray\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                        if pages_match:
                            try:
                                pages = json.loads(pages_match.group(1))
                                
                                images = []
                                for page in pages:
                                    page_num = page.get("Page")
                                    image_url = f"https://{path_name}/manga/{seriesId}/{directory}/{page_num}"
                                    images.append(image_url)
                                    
                                return {
                                    "seriesId": seriesId,
                                    "chapterId": chapterId,
                                    "images": images
                                }
                            except json.JSONDecodeError:
                                pass
                    except json.JSONDecodeError:
                        pass
        
        return {
            "seriesId": seriesId,
            "chapterId": chapterId,
            "images": []
        }
