import logging

from content_fetcher.plex_provider import PlexProvider
from content_fetcher.trakt_provider import TraktProvider
from content_fetcher.content_manager import ContentManager
from release_finder.torrentio_finder import Torrentio
from release_finder.release_finder_manager import ReleaseFinderManager

logger = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    setup_logging()

    manager = ContentManager()
#    manager.add_provider("Plex", PlexProvider())
    
    print("Initializing Trakt provider. You may need to authorize the application.")
    trakt_provider = TraktProvider()
    manager.add_provider("Trakt", trakt_provider)

    all_watchlists = manager.get_all_watchlists()

    for provider, watchlist in all_watchlists.items():
        logger.info(f"{provider} watchlist: {watchlist}")

    # Initialize ReleaseFinderManager and add Torrentio finder
    release_finder_manager = ReleaseFinderManager()
    release_finder_manager.add_finder("Torrentio", Torrentio())

    # Find releases for each item in the watchlist
    for provider, watchlist in all_watchlists.items():
        logger.info(f"Finding releases for {provider} watchlist:")
        for item in watchlist:
            imdb_id = item['imdb_id']
            media_type = item['media_type']
            title = item['title']
            year = item.get('year', 'N/A')

            logger.info(f"Searching for releases: {title} ({year}) - {media_type}")
            releases = release_finder_manager.find_releases("Torrentio", imdb_id, media_type)

            if releases:
                logger.info(f"Found {len(releases)} releases for {title}:")
                for release in releases:
                    logger.info(f"  - {release.title} (Hash: {release.infoHash}) (Size: {release.size_in_gb}GB) (Peers: {release.peers})")
            else:
                logger.info(f"No releases found for {title}")

            logger.info("---")

if __name__ == "__main__":
    main()
