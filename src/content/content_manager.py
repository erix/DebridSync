from typing import Dict, List, Protocol


class ContentProvider(Protocol):
    def get_watchlist(self) -> List[Dict[str, str]]: ...

    def remove_from_watchlist(self, item: Dict[str, str]) -> bool: ...

    def get_user_collection(self) -> List[Dict[str, str]]: ...

    def get_user_ratings(self) -> List[Dict[str, str]]: ...


class ContentManager:
    def __init__(self):
        self.providers: Dict[str, ContentProvider] = {}

    def add_provider(self, name: str, provider: ContentProvider):
        self.providers[name] = provider

    def get_watchlist(self, provider_name: str) -> List[Dict[str, str]]:
        provider = self.providers.get(provider_name)
        if provider:
            return provider.get_watchlist()
        else:
            raise ValueError(f"No provider found with name: {provider_name}")

    def get_all_watchlists(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            name: provider.get_watchlist() for name, provider in self.providers.items()
        }

    def get_provider(self, name: str) -> ContentProvider:
        """
        Get a content provider by name.

        Args:
            name (str): The name of the provider.

        Returns:
            ContentProvider: The requested content provider.

        Raises:
            KeyError: If the provider is not found.
        """
        if name not in self.providers:
            raise KeyError(f"Provider '{name}' not found")
        return self.providers[name]
