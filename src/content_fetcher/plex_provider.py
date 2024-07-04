import logging
from typing import List

from plexapi.myplex import MyPlexAccount

from content_fetcher.content_provider import ContentProvider
from content_fetcher.config import PLEX_PASSWORD, PLEX_USERNAME

logger = logging.getLogger(__name__)

class PlexProvider(ContentProvider):
    def __init__(self, username: str = PLEX_USERNAME, password: str = PLEX_PASSWORD):
        self.username = username
        self.password = password

    def get_watchlist(self) -> List[str]:
        try:
            account = MyPlexAccount(self.username, self.password)
            watchlist = account.watchlist()
            return [item.title for item in watchlist]
        except Exception as e:
            logger.error(f"Error fetching Plex watchlist: {e}")
            return []
