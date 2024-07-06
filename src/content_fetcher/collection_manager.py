from typing import Dict, List
from content_fetcher.media_collection_provider import MediaCollectionProvider

class CollectionManager:
    def __init__(self):
        self.providers: Dict[str, MediaCollectionProvider] = {}

    def add_provider(self, name: str, provider: MediaCollectionProvider):
        self.providers[name] = provider

    def get_provider(self, name: str) -> MediaCollectionProvider:
        if name not in self.providers:
            raise KeyError(f"Provider '{name}' not found")
        return self.providers[name]

    def get_user_collections(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            name: provider.get_user_collection()
            for name, provider in self.providers.items()
        }
