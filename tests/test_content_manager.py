import pytest
from unittest.mock import Mock

from content_fetcher.content_manager import ContentManager
from content_fetcher.content_provider import ContentProvider

class MockProvider(ContentProvider):
    def get_watchlist(self):
        return ["Test Movie 1", "Test Movie 2"]

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
    assert watchlist == ["Test Movie 1", "Test Movie 2"]

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
        "Test1": ["Test Movie 1", "Test Movie 2"],
        "Test2": ["Test Movie 1", "Test Movie 2"]
    }

