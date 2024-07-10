from abc import ABC, abstractmethod
from typing import List, Literal, Dict, Any
from models.release import Release


class Indexer(ABC):
    @abstractmethod
    def find_releases(
        self, imdb_id: str, media_type: Literal["movie", "show", "episode"], title: str
    ) -> List[Release]:
        """
        Find releases for a given IMDb ID and media type.

        Args:
            imdb_id (str): The IMDb ID of the movie, TV show, or episode.
            media_type (Literal['movie', 'show', 'episode']): The type of media, either 'movie', 'show', or 'episode'.

        Returns:
            List[Release]: A list of Release objects containing release information.
        """
        pass