from dataclasses import dataclass
from enum import Enum, auto

class MediaType(Enum):
    MOVIE = auto()
    SHOW = auto()
    EPISODE = auto()
    UNKNOWN = auto()

@dataclass
class Movie:
    title: str
    year: str
    imdb_id: str
    media_type: MediaType
