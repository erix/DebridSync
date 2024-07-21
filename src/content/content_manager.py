from typing import Dict, List, Protocol
from models.movie import Movie


class ContentProvider(Protocol):
    def get_watchlist(self) -> List[Movie]: ...
    def get_own_list(self, list_name: str) -> List[Movie]: ...
    def get_user_list(self, list_name: str) -> List[Movie]: ...
    def remove_from_watchlist(self, item: Dict[str, str]) -> bool: ...


class ContentManager:
    def __init__(self, config: Dict):
        self.providers: Dict[str, ContentProvider] = {}
        self.config = config

    def add_provider(self, name: str, provider: ContentProvider):
        self.providers[name] = provider

    def get_watchlist(self, provider_name: str, list_name: str = None) -> List[Movie]:
        provider = self.providers.get(provider_name)
        if provider:
            if provider_name == "trakt":
                if list_name == "watchlist":
                    return provider.get_watchlist()
                else:
                    return provider.get_own_list(list_name)
            elif provider_name == "plex":
                return provider.get_watchlist()
        else:
            raise ValueError(f"No provider found with name: {provider_name}")

    def get_all_watchlists(self) -> List[Movie]:
        all_movies = set()
        watchlists_config = self.config.get("watchlists", {})

        for provider_name, lists in watchlists_config.items():
            if provider_name == "trakt":
                trakt_provider = self.providers.get("trakt")
                if trakt_provider:
                    for list_type, list_names in lists.items():
                        if list_type == "user":
                            for list_name in list_names:
                                if list_name == "watchlist":
                                    all_movies.update(trakt_provider.get_watchlist())
                                else:
                                    all_movies.update(trakt_provider.get_own_list(list_name))
                        elif list_type == "public":
                            for list_name in list_names:
                                all_movies.update(trakt_provider.get_user_list(list_name))
            elif provider_name == "plex":
                plex_provider = self.providers.get("plex")
                if plex_provider and "watchlist" in lists:
                    all_movies.update(plex_provider.get_watchlist())

        return list(all_movies)

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
