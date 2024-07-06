import logging
import os

from content_fetcher.plex_provider import PlexProvider
from content_fetcher.trakt_provider import TraktProvider
from content_fetcher.content_manager import ContentManager
from release_finder.torrentio_finder import Torrentio
from release_finder.release_finder_manager import ReleaseFinderManager
from models.quality_profile import QualityProfile
from debrid.real_debrid import RealDebrid
from icecream import ic

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


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

    # Create a QualityProfile object
    quality_profile = QualityProfile(resolutions=["2160p", "1080p"])

    # Initialize RealDebrid client
    real_debrid_api_token = os.environ.get("REAL_DEBRID_API_TOKEN")
    if not real_debrid_api_token:
        logger.error("REAL_DEBRID_API_TOKEN environment variable is not set.")
        return

    real_debrid = RealDebrid(real_debrid_api_token)

    # Find releases for each item in the watchlist
    for provider, watchlist in all_watchlists.items():
        logger.info(f"Finding releases for {provider} watchlist:")
        for item in watchlist:
            imdb_id = item["imdb_id"]
            media_type = item["media_type"]
            title = item["title"]
            year = item.get("year", "N/A")

            logger.info(f"Searching for releases: {title} ({year}) - {media_type}")
            releases = release_finder_manager.find_releases(
                "Torrentio", imdb_id, media_type
            )
            ic(releases)

            if releases:
                logger.info(f"Found {len(releases)} releases for {title}")

                # Filter releases using the QualityProfile object
                filtered_releases = quality_profile.apply(releases)

                logger.info(f"Filtered to {len(filtered_releases)} releases:")
                for release in filtered_releases:
                    logger.info(
                        f"  - {release.title} (Hash: {release.infoHash}) (Size: {release.size_in_gb:.2f}GB) (Peers: {release.peers})"
                    )

                    # Add the torrent to Real-Debrid
                    try:
                        torrent_info = real_debrid.add_torrent(release.infoHash)
                        logger.info(
                            f"Added torrent to Real-Debrid: {torrent_info['id']}"
                        )

                        # Select all files for download
                        real_debrid.select_files(torrent_info["id"])
                        logger.info("Selected all files for download")

                        # Get torrent info
                        torrent_status = real_debrid.get_torrent_info(
                            torrent_info["id"]
                        )
                        logger.info(f"Torrent status: {torrent_status['status']}")
                    except Exception as e:
                        logger.error(f"Error adding torrent to Real-Debrid: {str(e)}")
            else:
                logger.info(f"No releases found for {title}")

            logger.info("---")


if __name__ == "__main__":
    main()
