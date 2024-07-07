# src/content_fetcher/trakt_provider.py

import json
import logging
import os
from typing import List, Dict
from threading import Condition

from trakt import Trakt
from trakt.core import exceptions
from trakt.objects import Movie, Show, Episode

from content_fetcher.content_provider import ContentProvider
from content_fetcher.media_collection_provider import MediaCollectionProvider

from icecream import ic


logger = logging.getLogger(__name__)


class TraktProvider(ContentProvider, MediaCollectionProvider):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = "trakt_token.json"

        self.is_authenticating = Condition()

        # Bind trakt events
        Trakt.on("oauth.token_refreshed", self._on_token_refreshed)

        self._configure_trakt()

    def _configure_trakt(self):
        Trakt.configuration.defaults.client(
            id=self.client_id, secret=self.client_secret
        )

        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                self.authorization = json.load(f)
            Trakt.configuration.defaults.oauth.from_response(self.authorization)
        else:
            self._device_auth()

    def _device_auth(self):
        if not self.is_authenticating.acquire(blocking=False):
            print("Authentication has already been started")
            return False

        # Request new device code
        code = Trakt["oauth/device"].code()

        print(
            f"Please go to {code['verification_url']} and enter the code: {code['user_code']}"
        )

        # Construct device authentication poller
        poller = (
            Trakt["oauth/device"]
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
            self.authorization = Trakt["oauth"].token_refresh(
                refresh_token=self.authorization["refresh_token"]
            )

            # Save the new token
            with open(self.token_file, "w") as f:
                json.dump(self.authorization, f)

            # Update the configuration with the new token. Refresh token if expired
            Trakt.configuration.defaults.oauth.from_response(
                self.authorization, refresh=True
            )

        except exceptions.RequestFailedError as e:
            print(f"Error refreshing token: {e}")
            # If refresh fails, we might need to re-authenticate
            os.remove(self.token_file)
            self._device_auth()

    def get_watchlist(self) -> List[Dict[str, str]]:
        try:
            logger.info("Getting watchlist for erix...")
            watchlist = Trakt["users/*/watchlist"].get(username="erix", extended="full")

            return [
                {
                    "title": item.title,
                    "year": str(item.year) if hasattr(item, "year") else "",
                    "imdb_id": item.get_key("imdb") if hasattr(item, "get_key") else "",
                    "media_type": self._get_media_type(item),
                }
                for item in watchlist
            ]
        except exceptions.RequestFailedError as e:
            if e.response.status_code == 401:  # Unauthorized, token might be expired
                logger.info("Token expired. Refreshing...")
                self._refresh_token()
                # Retry after refreshing
                watchlist = Trakt["users/*/watchlist"].get(
                    username="erix", extended="full"
                )
                return [
                    {
                        "title": item.title,
                        "year": str(item.year) if hasattr(item, "year") else "",
                        "imdb_id": item.get_key("imdb")
                        if hasattr(item, "get_key")
                        else "",
                        "media_type": self._get_media_type(item),
                    }
                    for item in watchlist
                ]
            else:
                logger.error(f"Error fetching Trakt watchlist: {e}")
                return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Trakt watchlist: {e}")
            return []

    def _get_media_type(self, item):
        if isinstance(item, Movie) or (hasattr(item, "type") and item.type == "movie"):
            return "movie"
        elif isinstance(item, Show) or (hasattr(item, "type") and item.type == "show"):
            return "show"
        elif isinstance(item, Episode) or (
            hasattr(item, "type") and item.type == "episode"
        ):
            return "episode"
        else:
            return "unknown"

    def remove_from_watchlist(self, item: Dict[str, str]) -> bool:
        logger.info(f"Log level is {logging.getLevelName(logger.getEffectiveLevel())}")
        try:
            # Assuming the item dictionary contains 'imdb_id' and 'media_type'
            imdb_id = item["imdb_id"]
            media_type = item["media_type"]

            if media_type == "movie":
                logger.debug(f"Delete movie from watchlist:{item['title']}")
                print(
                    Trakt["sync/watchlist"].remove(
                        {"movies": [{"ids": {"imdb": imdb_id}}]}
                    )
                )
            elif media_type in ["show", "episode"]:
                Trakt["sync/watchlist"].remove({"shows": [{"ids": {"imdb": imdb_id}}]})
            else:
                logger.error(f"Unknown media type: {media_type}")
                return False

            logger.info(f"Successfully removed {item['title']} from Trakt watchlist")
            return True
        except exceptions.RequestException as e:
            logger.error(f"Error removing item from Trakt watchlist: {e}")
            return False

    def get_user_collection(self) -> List[Dict[str, str]]:
        try:
            logger.info("Getting user collection...")
            movies = Trakt["sync/collection"].movies(extended="full")
            shows = Trakt["sync/collection"].shows(extended="full")
            # ic(movies)
            collection = []
            for item in movies:
                collection.append(item)

            for item in shows:
                collection.append(item)
            return collection

        except exceptions.RequestFailedError as e:
            logger.error(f"Error fetching Trakt user collection: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Trakt user collection: {e}")
            return []

    def _on_aborted(self):
        """Device authentication aborted.

        Triggered when device authentication was aborted (either with `DeviceOAuthPoller.stop()`
        or via the "poll" event)
        """

        print("Authentication aborted")

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

        print("Authentication successful - authorization: %r" % self.authorization)

        # Authentication complete
        self.is_authenticating.notify_all()
        self.is_authenticating.release()
        self._save_token()

    def _on_expired(self):
        """Device authentication expired."""

        print("Authentication expired")

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

        print("Token refreshed - authorization: %r" % self.authorization)

    def _save_token(self):
        with open(self.token_file, "w") as f:
            json.dump(self.authorization, f)
