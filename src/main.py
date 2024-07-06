import logging
import os

import yaml
from content_fetcher.content_manager import ContentManager
from content_fetcher.plex_provider import PlexProvider
from content_fetcher.trakt_provider import TraktProvider
from debrid.real_debrid import RealDebrid
from dotenv import load_dotenv
from icecream import ic
from models.quality_profile import QualityProfile
from release_finder.release_finder_manager import ReleaseFinderManager
from release_finder.torrentio_finder import Torrentio

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
    logging.basicConfig(
        level=config["logging"]["level"],
        format=config["logging"]["format"],
    )

def initialize_content_providers(config, env_vars):
    manager = ContentManager()
    content_providers = config.get('content_providers', {})
    for provider, settings in content_providers.items():
        if settings.get('enabled', False):
            if provider == 'trakt':
                print("Initializing Trakt provider. You may need to authorize the application.")
                trakt_provider = TraktProvider(
                    client_id=env_vars["TRAKT_CLIENT_ID"],
                    client_secret=env_vars["TRAKT_CLIENT_SECRET"],
                )
                manager.add_provider("Trakt", trakt_provider)
            elif provider == 'plex':
                plex_provider = PlexProvider(username=settings['username'], password=settings['password'])
                manager.add_provider("Plex", plex_provider)
    return manager

def initialize_release_finders(config):
    release_finder_manager = ReleaseFinderManager()
    release_finders = config.get('release_finders', {})
    for finder, settings in release_finders.items():
        if settings.get('enabled', False):
            if finder == 'torrentio':
                release_finder_manager.add_finder("Torrentio", Torrentio())
    return release_finder_manager

def process_watchlist_item(item, release_finder_manager, quality_profile, real_debrid, dry_run):
    imdb_id = item["imdb_id"]
    media_type = item["media_type"]
    title = item["title"]
    year = item.get("year", "N/A")

    logger.info(f"Searching for releases: {title} ({year}) - {media_type}")
    releases = release_finder_manager.find_releases("Torrentio", imdb_id, media_type)
    ic(releases)

    if releases:
        logger.info(f"Found {len(releases)} releases for {title}")
        filtered_releases = quality_profile.apply(releases)
        logger.info(f"Filtered to {len(filtered_releases)} releases:")
        
        for release in filtered_releases:
            logger.info(
                f"  - {release.title} (Hash: {release.infoHash}) (Size: {release.size_in_gb:.2f}GB) (Peers: {release.peers})"
            )
            add_torrent_to_real_debrid(release, real_debrid, dry_run)
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
        except Exception as e:
            logger.error(f"Error adding torrent to Real-Debrid: {str(e)}")
    else:
        logger.info(f"Dry run: Would have added torrent {release.infoHash} to Real-Debrid")

def main():
    config = load_config()
    env_vars = load_env_vars()
    setup_logging(config)

    dry_run = config.get('developer', {}).get('dry_run', False)
    if dry_run:
        logger.info("Running in dry run mode. No changes will be made to Real-Debrid.")

    content_manager = initialize_content_providers(config, env_vars)
    release_finder_manager = initialize_release_finders(config)
    quality_profile = QualityProfile(resolutions=config["quality_profile"]["resolutions"])

    real_debrid_api_token = config["real_debrid"]["api_token"]
    if not real_debrid_api_token:
        logger.error("Real-Debrid API token is not set in the configuration.")
        return

    real_debrid = RealDebrid(real_debrid_api_token)

    all_watchlists = content_manager.get_all_watchlists()
    for provider, watchlist in all_watchlists.items():
        logger.info(f"Finding releases for {provider} watchlist:")
        for item in watchlist:
            process_watchlist_item(item, release_finder_manager, quality_profile, real_debrid, dry_run)

if __name__ == "__main__":
    main()
