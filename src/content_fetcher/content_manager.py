from typing import Dict, List

from content_fetcher.content_provider import ContentProvider

class ContentManager:
    def __init__(self):
        self.providers: Dict[str, ContentProvider] = {}

    def add_provider(self, name: str, provider: ContentProvider):
        self.providers[name] = provider

    def get_watchlist(self, provider_name: str) -> List[str]:
        provider = self.providers.get(provider_name)
        if provider:
            return provider.get_watchlist()
        else:
            raise ValueError(f"No provider found with name: {provider_name}")

    def get_all_watchlists(self) -> Dict[str, List[str]]:
        return {name: provider.get_watchlist() for name, provider in self.providers.items()}

