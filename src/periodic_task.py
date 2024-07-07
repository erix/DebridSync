import schedule
import time
import logging

logger = logging.getLogger(__name__)


def start_periodic_task(
    interval,
    content_manager,
    collection_manager,
    release_finder_manager,
    quality_profile,
    real_debrid,
    dry_run,
    remove_after_adding,
):
    def job():
        logger.info("Running periodic check for new watchlist items")
        process_all_watchlists(
            content_manager,
            collection_manager,
            release_finder_manager,
            quality_profile,
            real_debrid,
            dry_run,
            remove_after_adding,
        )

    schedule.every(interval).seconds.do(job)

    logger.info(f"Scheduled periodic task to run every {interval} seconds")

    while True:
        schedule.run_pending()
        time.sleep(1)


def process_all_watchlists(
    content_manager,
    collection_manager,
    release_finder_manager,
    quality_profile,
    real_debrid,
    dry_run,
    remove_after_adding,
):
    all_watchlists = content_manager.get_all_watchlists()
    user_collections = collection_manager.get_user_collections()

    for provider, watchlist in all_watchlists.items():
        if not watchlist:
            logger.info(f"Empty watchilst for {provider}")
            continue
        logger.info(f"Checking for new items in {provider} watchlist")
        content_provider = content_manager.get_provider(provider)
        for item in watchlist:
            if not is_item_processed(item, user_collections):
                logger.info(f"Processing new item: {item['title']}")
                process_watchlist_item(
                    item,
                    release_finder_manager,
                    quality_profile,
                    real_debrid,
                    dry_run,
                    remove_after_adding,
                    content_provider,
                )


def is_item_processed(item, user_collection):
    return any(id == item["imdb_id"] for id in user_collection)


def process_watchlist_item(
    item,
    release_finder_manager,
    quality_profile,
    real_debrid,
    dry_run,
    remove_after_adding,
    content_provider,
):
    imdb_id = item["imdb_id"]
    media_type = item["media_type"]
    title = item["title"]
    year = item.get("year", "N/A")

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
