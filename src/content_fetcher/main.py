import logging

from content_fetcher.plex_provider import PlexProvider
from content_fetcher.trakt_provider import TraktProvider
from content_fetcher.content_manager import ContentManager

logger = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    setup_logging()

    manager = ContentManager()
    manager.add_provider("Plex", PlexProvider())
    manager.add_provider("Trakt", TraktProvider())

    all_watchlists = manager.get_all_watchlists()

    for provider, watchlist in all_watchlists.items():
        logger.info(f"{provider} watchlist: {watchlist}")

if __name__ == "__main__":
    main()
