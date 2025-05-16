from app.crud.user import user
from app.crud.manga import manga, chapter
from app.crud.bookmark import CRUDBookmark
from app.models.manga import Bookmark

bookmark = CRUDBookmark(Bookmark)
