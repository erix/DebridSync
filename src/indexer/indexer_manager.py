from typing import Dict
from .indexer import Indexer


class IndexerManager:
    def __init__(self):
        self.indexers: Dict[str, Indexer] = {}

    def add_indexer(self, name: str, indexer: Indexer):
        self.indexers[name] = indexer

    def get_indexer(self, name: str) -> Indexer:
        indexer = self.indexers.get(name)
        if indexer:
            return indexer
        else:
            raise ValueError(f"No indexer found with name: {name}")

    def find_releases(self, name: str, imdb_id: str, media_type: str):
        return self.get_indexer(name).find_releases(imdb_id, media_type)
