from abc import ABC, abstractmethod
from typing import List, Dict, Literal

class ReleaseFinder(ABC):
    @abstractmethod
    def find_releases(self, imdb_id: str, media_type: Literal['movie', 'show']) -> List[Dict[str, str]]:
        """
        Find releases for a given IMDb ID and media type.

        Args:
            imdb_id (str): The IMDb ID of the movie or TV show.
            media_type (Literal['movie', 'show']): The type of media, either 'movie' or 'show'.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing release information.
            Each dictionary contains the following keys:
                - title (str): The title of the release.
                - infoHash (str): The info hash of the torrent.
                - size_in_gb (float): The size of the release in gigabytes.
                - peers (int): The number of peers for the release.
        """
        pass
