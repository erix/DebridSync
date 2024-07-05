# src/content_fetcher/trakt_provider.py

import json
import logging
import os
from typing import List, Dict, Optional
from threading import Condition

from trakt import Trakt
from trakt.core import exceptions
from trakt.objects import Movie, Show, Episode

from content_fetcher.content_provider import ContentProvider
from content_fetcher.config import TRAKT_CLIENT_ID, TRAKT_CLIENT_SECRET

from icecream import ic

logger = logging.getLogger(__name__)

class TraktProvider(ContentProvider):
    def __init__(self, client_id: str = TRAKT_CLIENT_ID, client_secret: str = TRAKT_CLIENT_SECRET):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = 'trakt_token.json'

        self.is_authenticating = Condition()

        # Bind trakt events
        Trakt.on('oauth.token_refreshed', self.on_token_refreshed)

        self.configure_trakt()

    def configure_trakt(self):
        Trakt.configuration.defaults.client(id=self.client_id, secret=self.client_secret)

        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                self.authorization = json.load(f)
            Trakt.configuration.oauth.from_response(self.authorization)
        else:
            self.device_auth()

    def device_auth(self):
        if not self.is_authenticating.acquire(blocking=False):
            print('Authentication has already been started')
            return False

        # Request new device code
        code = Trakt['oauth/device'].code()

        print(f"Please go to {code['verification_url']} and enter the code: {code['user_code']}")

        # Construct device authentication poller
        poller = Trakt['oauth/device'].poll(**code)\
            .on('aborted', self.on_aborted)\
            .on('authenticated', self.on_authenticated)\
            .on('expired', self.on_expired)\
            .on('poll', self.on_poll)

        # Start polling for authentication token
        poller.start(daemon=False)

        # Wait for authentication to complete
        return self.is_authenticating.wait()

    def refresh_token(self):
        try:
            self.authorization = Trakt['oauth'].token_refresh(refresh_token=self.authorization['refresh_token'])
            
            # Save the new token
            with open(self.token_file, 'w') as f:
                json.dump(self.authorization, f)

            # Update the configuration with the new token. Refresh token if expired
            Trakt.configuration.oauth.from_response(self.authorization, refresh=True)

        except exceptions.RequestFailedError as e:
            print(f"Error refreshing token: {e}")
            # If refresh fails, we might need to re-authenticate
            os.remove(self.token_file)
            self.device_auth()

    def get_watchlist(self) -> List[Dict[str, str]]:
        try:
            watchlist = Trakt['users/*/watchlist'].get(username='erix', extended='full')
            [ic(item.to_dict()) for item in watchlist]

            return [
                {
                    'title': item.title,
                    'year': str(item.year) if hasattr(item, 'year') else '',
                    'imdb_id': item.get_key('imdb') if hasattr(item, 'get_key') else '',
                    'media_type': self._get_media_type(item)
                }
                for item in watchlist
            ]
        except exceptions.RequestFailedError as e:
            if e.response.status_code == 401:  # Unauthorized, token might be expired
                logger.info("Token expired. Refreshing...")
                self.refresh_token()
                # Retry after refreshing
                watchlist = Trakt['users/*/watchlist'].get(username='erix', extended='full')
                return [
                    {
                        'title': item.title,
                        'year': str(item.year) if hasattr(item, 'year') else '',
                        'imdb_id': item.get_key('imdb') if hasattr(item, 'get_key') else '',
                        'media_type': self._get_media_type(item)
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
        if isinstance(item, Movie):
            return 'movie'
        elif isinstance(item, Show):
            return 'show'
        elif isinstance(item, Episode):
            return 'episode'
        else:
            return 'unknown'

    def on_aborted(self):
        """Device authentication aborted.

        Triggered when device authentication was aborted (either with `DeviceOAuthPoller.stop()`
        or via the "poll" event)
        """

        print('Authentication aborted')

        # Authentication aborted
        self.is_authenticating.acquire()
        self.is_authenticating.notify_all()
        self.is_authenticating.release()

    def on_authenticated(self, authorization):
        """Device authenticated.

        :param authorization: Authentication token details
        :type authorization: dict
        """

        # Acquire condition
        self.is_authenticating.acquire()

        # Store authorization for future calls
        self.authorization = authorization

        print('Authentication successful - authorization: %r' % self.authorization)

        # Authentication complete
        self.is_authenticating.notify_all()
        self.is_authenticating.release()
        self.save_token()

    def on_expired(self):
        """Device authentication expired."""

        print('Authentication expired')

        # Authentication expired
        self.is_authenticating.acquire()
        self.is_authenticating.notify_all()
        self.is_authenticating.release()

    def on_poll(self, callback):
        """Device authentication poll.

        :param callback: Call with `True` to continue polling, or `False` to abort polling
        :type callback: func
        """

        # Continue polling
        callback(True)

    def on_token_refreshed(self, authorization):
        # OAuth token refreshed, store authorization for future calls
        self.authorization = authorization

        print('Token refreshed - authorization: %r' % self.authorization)

    def save_token(self):
        with open(self.token_file, 'w') as f:
            json.dump(self.authorization, f)
