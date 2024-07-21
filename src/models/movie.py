from dataclasses import dataclass
from enum import Enum, auto

class MediaType(Enum):
    MOVIE = auto()
    SHOW = auto()
    EPISODE = auto()
    UNKNOWN = auto()

@dataclass(frozen=True)
class Movie:
    def __hash__(self):
        return hash((self.title, self.year, self.imdb_id, self.media_type))

    def __eq__(self, other):
        if not isinstance(other, Movie):
            return NotImplemented
        return (self.title, self.year, self.imdb_id, self.media_type) == (other.title, other.year, other.imdb_id, other.media_type)
    title: str
    year: str
    imdb_id: str
    media_type: MediaType
