import logging
import os

import yaml
from content_fetcher.content_manager import ContentManager
from content_fetcher.collection_manager import CollectionManager
from content_fetcher.plex_provider import PlexProvider
from content_fetcher.trakt_provider import TraktProvider
from content_fetcher.media_collection_provider import MediaCollectionProvider
from debrid.real_debrid import RealDebrid
from dotenv import load_dotenv
from models.quality_profile import QualityProfile
from release_finder.release_finder_manager import ReleaseFinderManager
from release_finder.torrentio_finder import Torrentio

from icecream import ic


logger = logging.getLogger(__name__)


def load_config():
    with open("config.yml", "r") as config_file:
        return yaml.safe_load(config_file)


def load_env_vars():
    load_dotenv()
    return {
        "TRAKT_CLIENT_ID": os.getenv("TRAKT_CLIENT_ID"),
        "TRAKT_CLIENT_SECRET": os.getenv("TRAKT_CLIENT_SECRET"),
    }


def setup_logging(config):
    log_level_str = config["logging"]["level"].upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format=config["logging"]["format"],
    )
    logger.debug(f"Logging configured with level: {log_level_str}")


def initialize_content_providers(config, env_vars):
    content_manager = ContentManager()
    collection_manager = CollectionManager()
    content_providers = config.get("content_providers", {})
    for provider, settings in content_providers.items():
        if settings.get("enabled", False):
            if provider == "trakt":
                trakt_provider = TraktProvider(
                    client_id=env_vars["TRAKT_CLIENT_ID"],
                    client_secret=env_vars["TRAKT_CLIENT_SECRET"],
                )
                content_manager.add_provider("Trakt", trakt_provider)
                collection_manager.add_provider("Trakt", trakt_provider)
            elif provider == "plex":
                plex_provider = PlexProvider(
                    username=settings["username"], password=settings["password"]
                )
                content_manager.add_provider("Plex", plex_provider)
                collection_manager.add_provider("Plex", plex_provider)
    return content_manager, collection_manager


def initialize_release_finders(config):
    release_finder_manager = ReleaseFinderManager()
    release_finders = config.get("release_finders", {})
    for finder, settings in release_finders.items():
        if settings.get("enabled", False):
            if finder == "torrentio":
                release_finder_manager.add_finder("Torrentio", Torrentio())
    return release_finder_manager


def process_watchlist_item(
    item,
    release_finder_manager,
    quality_profile,
    real_debrid,
    dry_run,
    remove_after_adding,
    content_provider,
    user_collection,
):
    imdb_id = item["imdb_id"]
    media_type = item["media_type"]
    title = item["title"]
    year = item.get("year", "N/A")

    # Check if the item is already in the user's collection
    if any(
        id == imdb_id for key, id in user_collection
    ):
        logger.info(f"Skipping {title} ({year}) - Already in collection")
        return

    logger.info(f"Searching for releases: {title} ({year}) - {media_type}")
    releases = release_finder_manager.find_releases("Torrentio", imdb_id, media_type)

    if releases:
        logger.info(f"Found {len(releases)} releases for {title}")
        filtered_releases = quality_profile.apply(releases)
        logger.info(f"Filtered to {len(filtered_releases)} releases:")

        for release in filtered_releases:
            logger.info(
                f"  - {release.title} (Hash: {release.infoHash}) (Size: {release.size_in_gb:.2f}GB) (Peers: {release.peers})"
            )
            success = add_torrent_to_real_debrid(release, real_debrid, dry_run)
            if success and remove_after_adding and not dry_run:
                content_provider.remove_from_watchlist(item)
                logger.info(f"Removed {title} from watchlist")
            break  # Only process the first filtered release
    else:
        logger.info(f"No releases found for {title}")

    logger.info("---")


def add_torrent_to_real_debrid(release, real_debrid, dry_run):
    if not dry_run:
        try:
            torrent_info = real_debrid.add_torrent(release.infoHash)
            logger.info(f"Added torrent to Real-Debrid: {torrent_info['id']}")

            real_debrid.select_files(torrent_info["id"])
            logger.info("Selected all files for download")

            torrent_status = real_debrid.get_torrent_info(torrent_info["id"])
            logger.info(f"Torrent status: {torrent_status['status']}")
            return True
        except Exception as e:
            logger.error(f"Error adding torrent to Real-Debrid: {str(e)}")
            return False
    else:
        logger.info(
            f"Dry run: Would have added torrent {release.infoHash} to Real-Debrid"
        )
        return True


def main():
    config = load_config()
    env_vars = load_env_vars()
    setup_logging(config)

    dry_run = config.get("developer", {}).get("dry_run", False)
    remove_after_adding = config.get("watchlist", {}).get("remove_after_adding", False)
    if dry_run:
        logger.info(
            "Running in dry run mode. No changes will be made to Real-Debrid or watchlists."
        )

    content_manager, collection_manager = initialize_content_providers(config, env_vars)
    release_finder_manager = initialize_release_finders(config)
    quality_profile = QualityProfile(
        resolutions=config["quality_profile"]["resolutions"]
    )

    real_debrid_api_token = config["real_debrid"]["api_token"]
    if not real_debrid_api_token:
        logger.error("Real-Debrid API token is not set in the configuration.")
        return

    real_debrid = RealDebrid(real_debrid_api_token)

    all_watchlists = content_manager.get_all_watchlists()
    ic(all_watchlists.items())

    # Fetch user collections
    user_collections = collection_manager.get_user_collections()
    # ic(user_collections)

    for provider, watchlist in all_watchlists.items():
        logger.info(f"Finding releases for {provider} watchlist:")
        content_provider = content_manager.get_provider(provider)
        user_collection = user_collections.get(provider, [])
        for item in watchlist:
            process_watchlist_item(
                item,
                release_finder_manager,
                quality_profile,
                real_debrid,
                dry_run,
                remove_after_adding,
                content_provider,
                user_collection,
            )


if __name__ == "__main__":
    main()
