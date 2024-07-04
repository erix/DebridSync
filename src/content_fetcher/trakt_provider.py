import logging
from typing import List

from trakt import Trakt

from content_fetcher.content_provider import ContentProvider
from content_fetcher.config import TRAKT_CLIENT_ID, TRAKT_CLIENT_SECRET

logger = logging.getLogger(__name__)

class TraktProvider(ContentProvider):
    def __init__(self, client_id: str = TRAKT_CLIENT_ID, client_secret: str = TRAKT_CLIENT_SECRET):
        self.client_id = client_id
        self.client_secret = client_secret
        Trakt.configuration.client_id = self.client_id
        Trakt.configuration.client_secret = self.client_secret

    def get_watchlist(self) -> List[str]:
        try:
            with Trakt.configuration.oauth.from_config():
                watchlist = Trakt["users/me/watchlist"].get(extended="full")
                return [item.title for item in watchlist]
        except Exception as e:
            logger.error(f"Error fetching Trakt watchlist: {e}")
            return []
