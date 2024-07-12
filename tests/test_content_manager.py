import pytest
from unittest.mock import Mock
from typing import Dict, List

from content.content_manager import ContentManager, ContentProvider


class MockProvider(ContentProvider):
    def get_watchlist(self) -> List[Dict[str, str]]:
        return [{"title": "Test Movie 1", "year": "2023"}, {"title": "Test Movie 2", "year": "2022"}]

    def remove_from_watchlist(self, item: Dict[str, str]) -> bool:
        return True

    def get_user_collection(self) -> List[Dict[str, str]]:
        return [{"title": "Test Collection Movie", "year": "2022"}]

    def get_user_ratings(self) -> List[Dict[str, str]]:
        return [{"title": "Test Rated Movie", "year": "2021", "rating": "8"}]


def test_add_provider():
    manager = ContentManager()
    provider = MockProvider()
    manager.add_provider("Test", provider)
    assert "Test" in manager.providers


def test_get_watchlist():
    manager = ContentManager()
    provider = MockProvider()
    manager.add_provider("Test", provider)
    watchlist = manager.get_watchlist("Test")
    assert watchlist == [{"title": "Test Movie 1", "year": "2023"}, {"title": "Test Movie 2", "year": "2022"}]


def test_get_all_watchlists():
    manager = ContentManager()
    provider = MockProvider()
    manager.add_provider("Test", provider)
    all_watchlists = manager.get_all_watchlists()
    assert all_watchlists == {"Test": [{"title": "Test Movie 1", "year": "2023"}, {"title": "Test Movie 2", "year": "2022"}]}


def test_get_provider():
    manager = ContentManager()
    provider = MockProvider()
    manager.add_provider("Test", provider)
    assert manager.get_provider("Test") == provider
    with pytest.raises(KeyError):
        manager.get_provider("NonExistent")


def test_get_user_collection():
    manager = ContentManager()
    provider = MockProvider()
    manager.add_provider("Test", provider)
    collection = manager.get_provider("Test").get_user_collection()
    assert collection == [{"title": "Test Collection Movie", "year": "2022"}]


def test_get_user_ratings():
    manager = ContentManager()
    provider = MockProvider()
    manager.add_provider("Test", provider)
    ratings = manager.get_provider("Test").get_user_ratings()
    assert ratings == [{"title": "Test Rated Movie", "year": "2021", "rating": "8"}]


def test_get_watchlist_invalid_provider():
    manager = ContentManager()
    with pytest.raises(ValueError):
        manager.get_watchlist("Invalid")


def test_get_all_watchlists():
    manager = ContentManager()
    provider1 = MockProvider()
    provider2 = MockProvider()
    manager.add_provider("Test1", provider1)
    manager.add_provider("Test2", provider2)
    all_watchlists = manager.get_all_watchlists()
    assert all_watchlists == {
        "Test1": [{"title": "Test Movie 1", "year": "2023"}, {"title": "Test Movie 2", "year": "2022"}],
        "Test2": [{"title": "Test Movie 1", "year": "2023"}, {"title": "Test Movie 2", "year": "2022"}],
    }
