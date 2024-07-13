import logging
from typing import List, Dict
from models.movie import Movie, MediaType
from plexapi.server import PlexServer

from plexapi.myplex import MyPlexAccount

from icecream import ic

logger = logging.getLogger(__name__)


class PlexProvider:
    def __init__(self, token: str, server_url: str, library_name: str):
        self.token = token
        self.server_url = server_url
        self.library_name = library_name
        self.account = MyPlexAccount(token=self.token)
        self.server = PlexServer(self.server_url, self.token)
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
                    media_type=MediaType(self._get_media_type(item)),
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

    def _get_media_type(self, item) -> MediaType:
        if hasattr(item, "type"):
            media_type = item.type.lower()
            if media_type == "movie":
                return MediaType.MOVIE
            elif media_type == "show":
                return MediaType.SHOW
            elif media_type == "episode":
                return MediaType.EPISODE
        return MediaType.UNKNOWN

    def get_user_collection(self) -> List[Dict[str, str]]:
        try:
            logger.info(f"Fetching user library form: {self.library_name}")
            # Get the specified library
            library = self.server.library.section(self.library_name)

            # Fetch all items from the library
            all_items = library.all()

            return [
                {
                    "title": movie.title,
                    "year": str(movie.year) if movie.year else "",
                    "imdb_id": self._get_imdb_id(movie.guids),
                    "media_type": str(self._get_media_type(movie).name),
                }
                for movie in all_items
            ]
        except Exception as e:
            logger.error(f"Error fetching Plex user collection: {e}")
            return []
