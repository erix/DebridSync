import pytest
from unittest.mock import patch, MagicMock
from content_fetcher.trakt_provider import TraktProvider

@pytest.fixture
def mock_trakt():
    with patch('content_fetcher.trakt_provider.Trakt') as mock:
        yield mock

def test_get_watchlist_success(mock_trakt):
    mock_item = MagicMock()
    mock_item.title = "Test Show"
    mock_trakt.__getitem__.return_value.get.return_value = [mock_item]

    provider = TraktProvider("test_id", "test_secret")
    result = provider.get_watchlist()

    assert result == ["Test Show"]

def test_get_watchlist_failure(mock_trakt):
    mock_trakt.__getitem__.return_value.get.side_effect = Exception("Test error")

    provider = TraktProvider("test_id", "test_secret")
    result = provider.get_watchlist()

    assert result == []
