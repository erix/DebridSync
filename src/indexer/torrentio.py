from typing import List, Dict, Any
import re
import requests
import logging

from models.release import Release
from models.movie import MediaType

from icecream import ic

logger = logging.getLogger(__name__)


class Torrentio:
    def __init__(self):
        self.base_url = "https://torrentio.strem.fun/sort=qualitysize&qualityfilter=480p,scr,cam/stream/"

    def find_releases(
        self, imdb_id: str, media_type: MediaType, title: str
    ) -> List[Release]:
        """
        Find releases for a given IMDb ID and media type using Torrentio.

        Args:
            imdb_id (str): The IMDb ID of the movie, TV show, or episode.
            media_type (MediaType): The type of media (MOVIE, SHOW, or EPISODE).
            title (str): The title of the movie or show.

        Returns:
            List[Release]: A list of Release objects containing release information.

        Raises:
            ValueError: If an invalid media_type is provided.
        """
        if media_type not in [MediaType.MOVIE, MediaType.SHOW, MediaType.EPISODE]:
            raise ValueError(
                f"Invalid media_type: {media_type}. Must be MediaType.MOVIE, MediaType.SHOW, or MediaType.EPISODE."
            )

        url = self._get_url(imdb_id, media_type)
        response = requests.get(url)
        data = response.json()

        releases = []
        for stream in data.get("streams", []):
            parsed_data = self._parse_title(stream["title"])
            release = Release(
                title=parsed_data["title"],
                infoHash=stream["infoHash"],
                size_in_gb=parsed_data["size_in_gb"],
                peers=parsed_data["peers"],
            )
            releases.append(release)
        return releases

    def _get_url(self, imdb_id: str, media_type: MediaType) -> str:
        if media_type == MediaType.MOVIE:
            return f"{self.base_url}movie/{imdb_id}.json"
        elif media_type == MediaType.SHOW:
            return f"{self.base_url}series/{imdb_id}:1:1.json"
        elif media_type == MediaType.EPISODE:
            return f"{self.base_url}series/{imdb_id}.json"
        else:
            raise ValueError(f"Unsupported media_type: {media_type}")

    def _parse_title(self, title: str) -> Dict[str, Any]:
        title_parts = title.split("\n")
        parsed_title = title_parts[0] if title_parts else ""

        size_match = re.search(r"💾\s*([\d.]+)\s*(GB|MB)", title)
        size_in_gb = 0
        if size_match:
            size = float(size_match.group(1))
            unit = size_match.group(2)
            size_in_gb = size if unit == "GB" else round(size / 1024, 2)

        peers_match = re.search(r"👤\s*(\d+)", title)
        peers = int(peers_match.group(1)) if peers_match else 0

        quality_match = re.search(r"(4K|2160p|1080p|720p|480p)", parsed_title)
        quality = quality_match.group(1) if quality_match else ""

        return {
            "title": parsed_title,
            "size_in_gb": size_in_gb,
            "peers": peers,
            "quality": quality,
        }
