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
            List[Dict[str, str]]: A list of dictionaries containing release information.
        """
        pass
