from typing import List, Literal, Dict, Any
import re
import requests
import logging
from typing import List, Literal

from .indexer import Indexer
from models.release import Release

from icecream import ic

logger = logging.getLogger(__name__)


class Torrentio(Indexer):
    def __init__(self):
        self.base_url = "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/stream/"

    def find_releases(
        self, imdb_id: str, media_type: Literal["movie", "show", "episode"], title: str
    ) -> List[Release]:
        """
        Find releases for a given IMDb ID and media type using Torrentio.

        Args:
            imdb_id (str): The IMDb ID of the movie, TV show, or episode.
            media_type (Literal['movie', 'show', 'episode']): The type of media, either 'movie', 'show', or 'episode'.
            title (str): The title of the movie or show.

        Returns:
            List[Release]: A list of Release objects containing release information.

        Raises:
            ValueError: If an invalid media_type is provided.
        """
        if media_type not in ["movie", "show", "episode"]:
            raise ValueError(
                "Invalid media_type. Must be 'movie', 'show', or 'episode'."
            )

        url = self._get_url(imdb_id, media_type)
        response = requests.get(url)
        data = response.json()
        ic(data)

        releases = []
        for stream in data.get("streams", []):
            release = Release(
                title=stream["title"],
                infoHash=stream["infoHash"],
                size_in_gb=self._parse_size(stream["title"]),
                peers=self._parse_peers(stream["title"]),
            )

            releases.append(release)
        return releases

    def _get_url(self, imdb_id: str, media_type: str) -> str:
        if media_type == "movie":
            return f"{self.base_url}movie/{imdb_id}.json"
        elif media_type == "show":
            return f"{self.base_url}series/{imdb_id}:1:1.json"
        else:  # episode
            return f"{self.base_url}series/{imdb_id}.json"

    def _parse_size(self, title: str) -> float:
        size_match = re.search(r"💾\s*([\d.]+)\s*(GB|MB)", title)
        if size_match:
            size = float(size_match.group(1))
            unit = size_match.group(2)
            return size if unit == "GB" else round(size / 1024, 2)
        return 0

    def _parse_peers(self, title: str) -> int:
        peers_match = re.search(r"👤\s*(\d+)", title)
        return int(peers_match.group(1)) if peers_match else 0

    def _parse_quality(self, title: str) -> str:
        quality_match = re.search(r"(4K|2160p|1080p|720p|480p)", title)
        return quality_match.group(1) if quality_match else ""
