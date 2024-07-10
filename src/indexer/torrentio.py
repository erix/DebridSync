import requests
from typing import List, Literal, Dict, Any
import re
import requests
import logging

from .indexer import Indexer
from models.release import Release
from RTN import RTN, SettingsModel, title_match, parse
from RTN.models import CustomRank, BaseRankingModel

from icecream import ic

logger = logging.getLogger(__name__)


class MyRankingModel(BaseRankingModel):
    uhd: int = 200  # Ultra HD content
    hdr: int = 100  # HDR content
    # Define more attributes and scores as needed


class Torrentio(Indexer):
    def __init__(self):
        self.settings = SettingsModel(
            require=["1080p", "4K"],
            exclude=[],
            preferred=["HDR", "BluRay", "Remux"],
        )
        self.rtn = RTN(settings=self.settings, ranking_model=MyRankingModel())

    def find_releases(
        self, imdb_id: str, media_type: Literal["movie", "show", "episode"], title: str
    ) -> List[Release]:
        """
        Find releases for a given IMDb ID and media type using Torrentio.

        Args:
            imdb_id (str): The IMDb ID of the movie, TV show, or episode.
            media_type (Literal['movie', 'show', 'episode']): The type of media, either 'movie', 'show', or 'episode'.

        Returns:
            List[Release]: A list of Release objects containing release information.

        Raises:
            ValueError: If an invalid media_type is provided.
        """
        if media_type not in ["movie", "show", "episode"]:
            raise ValueError(
                "Invalid media_type. Must be 'movie', 'show', or 'episode'."
            )

        base_url = "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/stream/"

        if media_type == "movie":
            url = f"{base_url}movie/{imdb_id}.json"
        elif media_type == "show":
            url = f"{base_url}series/{imdb_id}:1:1.json"
        else:  # episode
            url = f"{base_url}series/{imdb_id}.json"

        response = requests.get(url)
        data = response.json()

        releases = []
        for stream in data.get("streams", []):
            parsed = parse(stream["title"])
            if not stream["infoHash"] or not title_match(title, parsed.parsed_title):
                logger.debug(
                    f"Torrent skipped as it does not match the movie {stream["title"]}"
                )
                continue

            torrent = self.rtn.rank(stream["title"], stream["infoHash"])
            if torrent.fetch:
                release = Release(
                    # title=stream["title"],
                    title=torrent.data.parsed_title,
                    infoHash=stream["infoHash"],
                    size_in_gb=self._parse_size(stream["title"]),
                    peers=self._parse_peers(stream["title"]),
                    rank=torrent.rank if torrent.data.resolution else 0,
                )
                releases.append(release)
                ic(torrent)

        return sorted(releases, key=lambda x: x.rank, reverse=True)

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
