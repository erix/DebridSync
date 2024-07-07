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
