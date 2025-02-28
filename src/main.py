import logging
import os
import time

import schedule
import yaml
from content.collection_manager import CollectionManager
from content.content_manager import ContentManager
from content.plex_provider import PlexProvider
from content.trakt_provider import TraktProvider
from debrid.real_debrid import RealDebrid
from dotenv import load_dotenv
from icecream import ic
from indexer.indexer_manager import IndexerManager
from indexer.torrentio import Torrentio
from RTN import RTN, SettingsModel, parse, title_match
from RTN.models import BaseRankingModel
from models.movie import Movie

logger = logging.getLogger(__name__)

# Global variable to store processed movies
processed_movies = []


def load_config():
    with open("config.yml", "r") as config_file:
        config = yaml.safe_load(config_file)
    return config


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


def initialize_content_providers(config, trakt):
    content_manager = ContentManager(config)
    collection_manager = CollectionManager()
    media_library = config.get("media_library", {})
    watchlists = config.get("watchlists", {})
    plex_provider = None

    plex_libraries = media_library.get("plex_libraries", [])

    plex_config = config.get("plex", {})
    if plex_config:
        plex_provider = PlexProvider(
            token=plex_config.get("token"),
            server_url=plex_config.get("server_url"),
            library_name=plex_libraries[0] if plex_libraries else None,
        )

    if "trakt" in watchlists:
        logger.info("Added Trakt provider")
        content_manager.add_provider("trakt", trakt)

    if "plex" in watchlists and plex_provider:
        logger.info("Added Plex provider")
        content_manager.add_provider("plex", plex_provider)

    if media_library.get("trakt_collection", False):
        collection_manager.add_provider("Trakt", trakt)

    if plex_libraries and plex_provider:
        collection_manager.add_provider("Plex", plex_provider)

    return content_manager, collection_manager


def initialize_indexers(config):
    indexer_manager = IndexerManager()
    indexers = config.get("indexers", {})
    for indexer, settings in indexers.items():
        if settings.get("enabled", False):
            if indexer == "torrentio":
                indexer_manager.add_indexer("Torrentio", Torrentio())
    return indexer_manager


def is_item_processed(item: Movie, user_collection):
    global processed_movies
    return any(movie["imdb_id"] == item.imdb_id for movie in user_collection) or any(
        movie.imdb_id == item.imdb_id for movie in processed_movies
    )


def process_watchlist_item(
    item: Movie,
    indexer_manager,
    real_debrid,
    dry_run,
    trakt,
    rtn,
):
    global processed_movies
    imdb_id = item.imdb_id
    media_type = item.media_type
    title = item.title
    year = item.year if item.year else "N/A"

    # Check if the item has been released using TraktProvider
    is_released = trakt.check_released(item)
    if not is_released:
        logger.info(f"{title} ({year}) has not been released yet. Skipping.")
        return

    logger.info(f"Searching for releases: {title} ({year}) - {media_type}")
    releases = indexer_manager.find_releases("Torrentio", imdb_id, media_type, title)

    if releases:
        logger.info(f"Found {len(releases)} releases for {title}")

        ranked_releases = []
        for release in releases:
            parsed = parse(release.title)
            parsed_title = f"{parsed.parsed_title} ({parsed.year})"
            movie_title = f"{title} ({year})"
            if not title_match(parsed_title, movie_title, threshold=0.7):
                logger.debug(f"Skipping wrong match torrent: {parsed.parsed_title}")
                continue
            ranked_torrent = rtn.rank(release.title, release.infoHash)
            if ranked_torrent.fetch:
                release.rank = ranked_torrent.rank
                ranked_releases.append(release)
            else:
                logger.debug(f"Skipping garbage torrent: {release.title}")

        if not ranked_releases:
            logger.info(f"No downloadable relase found for {title}")
            return

        # Sort releases by rank in descending order
        ranked_releases.sort(key=lambda x: x.rank, reverse=True)

        for release in ranked_releases:
            logger.info(
                f"  - {release.title} (Hash: {release.infoHash}) (Size: {release.size_in_gb:.2f}GB) (Peers: {release.peers}) (Rank: {release.rank})"
            )
            success = add_torrent_to_real_debrid(release, real_debrid, dry_run)
            if success:
                processed_movies.append(item)

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


def process_all_watchlists(
    content_manager,
    collection_manager,
    indexer_manager,
    real_debrid,
    dry_run,
    trakt,
    rtn,
):
    all_watchlists = content_manager.get_all_watchlists()
    user_collections = collection_manager.get_user_collections()

    for item in all_watchlists:
        if not is_item_processed(item, user_collections["Plex"]):
            logger.info(f"Processing new item: {item.title}")
            process_watchlist_item(
                item,
                indexer_manager,
                real_debrid,
                dry_run,
                trakt,
                rtn,
            )
        else:
            logger.debug(f"Skipping already processed item: {item.title}")


def main():
    config = load_config()
    env_vars = load_env_vars()
    setup_logging(config)

    logger.info("Loaded configuration:")
    logger.info(yaml.dump(config, default_flow_style=False))

    dry_run = config.get("developer", {}).get("dry_run", False)
    if dry_run:
        logger.info("Running in dry run mode. No changes will be made to Real-Debrid.")

    trakt = TraktProvider(
        client_id=env_vars["TRAKT_CLIENT_ID"],
        client_secret=env_vars["TRAKT_CLIENT_SECRET"],
    )

    content_manager, collection_manager = initialize_content_providers(config, trakt)
    indexer_manager = initialize_indexers(config)

    real_debrid_api_token = config["real_debrid"]["api_token"]
    if not real_debrid_api_token:
        logger.error("Real-Debrid API token is not set in the configuration.")
        return

    real_debrid = RealDebrid(real_debrid_api_token)

    # Initialize RTN
    torrent_settings = config.get("torrent_settings", {})
    settings = SettingsModel(
        require=torrent_settings.get("require", []),
        exclude=torrent_settings.get("exclude", []),
        preferred=torrent_settings.get("preferred", []),
    )

    class ConfigRankingModel(BaseRankingModel):
        pass

    ranking_model_config = config.get("torrent_settings", {}).get("ranking_model", {})
    for attr, value in ranking_model_config.items():
        setattr(ConfigRankingModel, attr, value)

    rtn = RTN(settings=settings, ranking_model=ConfigRankingModel())

    # Start the periodic task
    check_interval = config.get("watchlist", {}).get(
        "check_interval", 3600
    )  # Default to 1 hour

    # periodic execution
    schedule.every(check_interval).seconds.do(
        process_all_watchlists,
        content_manager=content_manager,
        collection_manager=collection_manager,
        indexer_manager=indexer_manager,
        real_debrid=real_debrid,
        dry_run=dry_run,
        trakt=trakt,
        rtn=rtn,
    )

    # run immediately
    schedule.run_all()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
