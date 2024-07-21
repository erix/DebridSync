# src/content_fetcher/trakt_provider.py

import json
import logging
import os
from typing import List, Dict
from datetime import datetime
from functools import wraps

from models.movie import Movie, MediaType
from threading import Condition

import trakt

from icecream import ic


logger = logging.getLogger(__name__)


def require_auth(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "authorization") or not self.authorization:
            self._device_auth()
        return func(self, *args, **kwargs)

    return wrapper


class TraktProvider:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = "trakt_token.json"

        self.is_authenticating = Condition()

        # Bind trakt events
        trakt.Trakt.on("oauth.token_refreshed", self._on_token_refreshed)

        self._configure_trakt()
        logger.debug("Trakt initialized")

    def _configure_trakt(self):
        trakt.Trakt.configuration.defaults.client(
            id=self.client_id, secret=self.client_secret
        )

        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                self.authorization = json.load(f)
            trakt.Trakt.configuration.defaults.oauth.from_response(self.authorization)

    def _device_auth(self):
        if not self.is_authenticating.acquire(blocking=False):
            logger.debug("Authentication has already been started")
            return False

        # Request new device code
        code = trakt.Trakt["oauth/device"].code()

        logger.info(
            f"Please go to {code['verification_url']} and enter the code: {code['user_code']}"
        )

        # Construct device authentication poller
        poller = (
            trakt.Trakt["oauth/device"]
            .poll(**code)
            .on("aborted", self._on_aborted)
            .on("authenticated", self._on_authenticated)
            .on("expired", self._on_expired)
            .on("poll", self._on_poll)
        )

        # Start polling for authentication token
        poller.start(daemon=False)

        # Wait for authentication to complete
        return self.is_authenticating.wait()

    def _refresh_token(self):
        try:
            self.authorization = trakt.Trakt["oauth"].token_refresh(
                refresh_token=self.authorization["refresh_token"]
            )

            # Save the new token
            with open(self.token_file, "w") as f:
                json.dump(self.authorization, f)

            # Update the configuration with the new token. Refresh token if expired
            trakt.Trakt.configuration.defaults.oauth.from_response(
                self.authorization, refresh=True
            )

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            # If refresh fails, we might need to re-authenticate
            os.remove(self.token_file)
            self._device_auth()

    @require_auth
    def get_watchlist(self) -> List[Movie]:
        try:
            logger.info("Getting own watchlist...")
            watchlist = trakt.Trakt["users/me/watchlist"].get(extended="full")

            retval = [
                Movie(
                    title=item.title,
                    year=str(item.year) if hasattr(item, "year") else "",
                    imdb_id=item.get_key("imdb") if hasattr(item, "get_key") else "",
                    media_type=MediaType(self._get_media_type(item)),
                )
                for item in watchlist
            ]
            return retval
        except trakt.core.exceptions.RequestFailedError as e:
            if e.response.status_code == 401:  # Unauthorized, token might be expired
                logger.info("Token expired. Refreshing...")
                self._refresh_token()
                # Retry after refreshing
                watchlist = trakt.Trakt["users/me/watchlist"].get(extended="full")
                return [
                    Movie(
                        title=item.title,
                        year=str(item.year) if hasattr(item, "year") else "",
                        imdb_id=item.get_key("imdb")
                        if hasattr(item, "get_key")
                        else "",
                        media_type=self._get_media_type(item),
                    )
                    for item in watchlist
                ]
            else:
                logger.error(f"Error fetching Trakt watchlist: {e}")
                return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Trakt watchlist: {e}")
            return []

    @require_auth
    def get_own_list(self, list_name: str) -> List[Movie]:
        try:
            logger.info(f"Getting {list_name} list...")
            watchlist = trakt.Trakt[f"users/me/lists/{list_name}"].get()
            if not watchlist.items():
                logger.debug(f"Empty list {list_name}")
                return []

            retval = [
                Movie(
                    title=item.title,
                    year=str(item.year) if hasattr(item, "year") else "",
                    imdb_id=item.get_key("imdb") if hasattr(item, "get_key") else "",
                    media_type=MediaType(self._get_media_type(item)),
                )
                for item in watchlist.items()
            ]
            return retval
        except Exception as e:
            logger.error(f"Unexpected error fetching Trakt watchlist: {e}")
            return []

    def get_user_list(self, list_name: str) -> List[Movie]:
        try:
            logger.info(f"Getting {list_name} ...")
            watchlist = trakt.Trakt[f"users/{list_name}"].get()
            if not watchlist.items():
                logger.debug(f"Empty list {list_name}")
                return []

            retval = [
                Movie(
                    title=item.title,
                    year=str(item.year) if hasattr(item, "year") else "",
                    imdb_id=item.get_key("imdb") if hasattr(item, "get_key") else "",
                    media_type=MediaType(self._get_media_type(item)),
                )
                for item in watchlist.items()
            ]
            return retval
        except Exception as e:
            logger.error(f"Unexpected error fetching Trakt watchlist: {e}")
            return []

    def _get_media_type(self, item) -> MediaType:
        if isinstance(item, trakt.objects.Movie) or (
            hasattr(item, "type") and item.type == "movie"
        ):
            return MediaType.MOVIE
        elif isinstance(item, trakt.objects.Show) or (
            hasattr(item, "type") and item.type == "show"
        ):
            return MediaType.SHOW
        elif isinstance(item, trakt.objects.Episode) or (
            hasattr(item, "type") and item.type == "episode"
        ):
            return MediaType.EPISODE
        else:
            return MediaType.UNKNOWN

    @require_auth
    def remove_from_watchlist(self, item: Dict[str, str]) -> bool:
        logger.info(f"Log level is {logging.getLevelName(logger.getEffectiveLevel())}")
        try:
            # Assuming the item dictionary contains 'imdb_id' and 'media_type'
            imdb_id = item["imdb_id"]
            media_type = item["media_type"]

            if media_type == "movie":
                logger.debug(f"Delete movie from watchlist:{item['title']}")
                logger.debug(
                    trakt.Trakt["sync/watchlist"].remove(
                        {"movies": [{"ids": {"imdb": imdb_id}}]}
                    )
                )
            elif media_type in ["show", "episode"]:
                trakt.Trakt["sync/watchlist"].remove(
                    {"shows": [{"ids": {"imdb": imdb_id}}]}
                )
            else:
                logger.error(f"Unknown media type: {media_type}")
                return False

            logger.info(f"Successfully removed {item['title']} from Trakt watchlist")
            return True
        except trakt.core.exceptions.RequestException as e:
            logger.error(f"Error removing item from Trakt watchlist: {e}")
            return False

    @require_auth
    def get_user_collection(self) -> List[Dict[str, str]]:
        try:
            logger.info("Getting user collection...")
            movies = trakt.Trakt["sync/collection"].movies(extended="full")
            shows = trakt.Trakt["sync/collection"].shows(extended="full")
            collection = []
            for item in movies + shows:
                collection.append(
                    {
                        "title": item.title,
                        "year": str(item.year) if hasattr(item, "year") else "",
                        "imdb_id": item.get_key("imdb")
                        if hasattr(item, "get_key")
                        else "",
                        "media_type": self._get_media_type(item),
                    }
                )
            return collection
        except Exception as e:
            logger.error(f"Error fetching Trakt user collection: {e}")
            return []

    def check_released(self, movie: Movie) -> bool:
        try:
            logger.info(f"Checking release status for: {movie.title}")

            response = trakt.Trakt.http.get(f"movies/{movie.imdb_id}/releases/us")
            if response.ok:
                release_data = response.json()
                today = datetime.now().date()
                digital_released = False
                physical_released = False

                for release in release_data:
                    release_date = datetime.strptime(
                        release["release_date"], "%Y-%m-%d"
                    ).date()
                    if release_date <= today:
                        if release["release_type"] == "digital":
                            logger.info(f"{movie.title} has been digitally released.")
                            digital_released = True
                        elif release["release_type"] == "physical":
                            logger.info(f"{movie.title} has been physically released.")
                            physical_released = True

                if not digital_released and not physical_released:
                    logger.info(f"{movie.title} has not been released yet.")

                return digital_released or physical_released
        except Exception as e:
            logger.error(f"Error fetching movie release data: {e}")
            return True

    def _on_aborted(self):
        """Device authentication aborted.

        Triggered when device authentication was aborted (either with `DeviceOAuthPoller.stop()`
        or via the "poll" event)
        """

        logger.debug("Authentication aborted")

        # Authentication aborted
        self.is_authenticating.acquire()
        self.is_authenticating.notify_all()
        self.is_authenticating.release()

    def _on_authenticated(self, authorization):
        """Device authenticated.

        :param authorization: Authentication token details
        :type authorization: dict
        """

        # Acquire condition
        self.is_authenticating.acquire()

        # Store authorization for future calls
        self.authorization = authorization
        trakt.Trakt.configuration.defaults.oauth.from_response(self.authorization)

        logger.info(
            "Authentication successful - authorization: %r" % self.authorization
        )

        # Authentication complete
        self.is_authenticating.notify_all()
        self.is_authenticating.release()
        self._save_token()

    def _on_expired(self):
        """Device authentication expired."""

        logger.debug("Authentication expired")

        # Authentication expired
        self.is_authenticating.acquire()
        self.is_authenticating.notify_all()
        self.is_authenticating.release()

    def _on_poll(self, callback):
        """Device authentication poll.

        :param callback: Call with `True` to continue polling, or `False` to abort polling
        :type callback: func
        """

        # Continue polling
        callback(True)

    def _on_token_refreshed(self, authorization):
        # OAuth token refreshed, store authorization for future calls
        self.authorization = authorization

        logger.debug("Token refreshed - authorization: %r" % self.authorization)

    def _save_token(self):
        with open(self.token_file, "w") as f:
            json.dump(self.authorization, f)
