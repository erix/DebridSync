import os
from dotenv import load_dotenv

load_dotenv()

PLEX_USERNAME = os.getenv("PLEX_USERNAME")
PLEX_PASSWORD = os.getenv("PLEX_PASSWORD")
TRAKT_CLIENT_ID = os.getenv("TRAKT_CLIENT_ID")
TRAKT_CLIENT_SECRET = os.getenv("TRAKT_CLIENT_SECRET")

