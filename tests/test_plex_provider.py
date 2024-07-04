import pytest
from unittest.mock import patch, MagicMock
from content_fetcher.plex_provider import PlexProvider

@pytest.fixture
def mock_plex_account():
    with patch('content_fetcher.plex_provider.MyPlexAccount') as mock:
        yield mock

def test_get_watchlist_success(mock_plex_account):
    mock_item = MagicMock()
    mock_item.title = "Test Movie"
    mock_plex_account.return_value.watchlist.return_value = [mock_item]

    provider = PlexProvider("test_user", "test_pass")
    result = provider.get_watchlist()

    assert result == ["Test Movie"]
    mock_plex_account.assert_called_once_with("test_user", "test_pass")

def test_get_watchlist_failure(mock_plex_account):
    mock_plex_account.side_effect = Exception("Test error")

    provider = PlexProvider("test_user", "test_pass")
    result = provider.get_watchlist()

    assert result == []
