import logging
from typing import List, Dict
from models.movie import Movie

from plexapi.myplex import MyPlexAccount

from icecream import ic

logger = logging.getLogger(__name__)


class PlexProvider:
    def __init__(self, token: str):
        self.token = token
        self.account = MyPlexAccount(token=self.token)
        logger.debug("Plex initialized")

    def get_watchlist(self) -> List[Movie]:
        try:
            watchlist = self.account.watchlist(libtype="movie")
            ic(watchlist)
            return [
                Movie(
                    title=item.title,
                    year=str(item.year) if hasattr(item, "year") else "",
                    imdb_id=self._get_imdb_id(item.guids),
                    media_type=self._get_media_type(item),
                )
                for item in watchlist
            ]
        except Exception as e:
            logger.error(f"Error fetching Plex watchlist: {e}")
            return []

    def remove_from_watchlist(self, item: Dict[str, str]) -> bool:
        # Implement the logic to remove an item from the Plex watchlist
        # This is a placeholder implementation
        logger.info(f"Removing item from Plex watchlist: {item['title']}")
        return True

    def _get_imdb_id(self, ids: List[str]) -> str:
        for id in ids:
            try:
                provider, id_value = id.id.split("://")
                if provider == "imdb":
                    return id_value
            except ValueError:
                return ""
        return ""

    def _get_media_type(self, item) -> str:
        if hasattr(item, "type"):
            return item.type.lower()
        return "unknown"
