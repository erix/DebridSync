from typing import Dict
from .release_finder import ReleaseFinder

class ReleaseFinderManager:
    def __init__(self):
        self.finders: Dict[str, ReleaseFinder] = {}

    def add_finder(self, name: str, finder: ReleaseFinder):
        self.finders[name] = finder

    def get_finder(self, name: str) -> ReleaseFinder:
        finder = self.finders.get(name)
        if finder:
            return finder
        else:
            raise ValueError(f"No release finder found with name: {name}")

    def find_releases(self, name: str, imdb_id: str, media_type: str):
        return self.get_finder(name).find_releases(imdb_id, media_type)
