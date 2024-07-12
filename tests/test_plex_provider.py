import pytest
from unittest.mock import patch, MagicMock
from content.plex_provider import PlexProvider
from models.movie import Movie


@pytest.fixture
def mock_plex_account():
    with patch("content.plex_provider.MyPlexAccount") as mock:
        yield mock


def test_get_watchlist_success(mock_plex_account):
    mock_item = MagicMock()
    mock_item.title = "Test Movie"
    mock_item.year = 2023
    mock_item.guid = "plex://movie/5d776b9ad6acaf001f8b4567"
    mock_item.guids = [MagicMock(id="imdb://tt1234567")]
    mock_item.type = "movie"
    mock_plex_account.return_value.watchlist.return_value = [mock_item]

    provider = PlexProvider("test_token")
    result = provider.get_watchlist()

    assert result == [
        Movie(
            title="Test Movie",
            year="2023",
            imdb_id="tt1234567",
            media_type="movie",
        )
    ]
    mock_plex_account.assert_called_once_with(token="test_token")


def test_get_watchlist_failure(mock_plex_account):
    mock_plex_account.return_value.watchlist.side_effect = Exception("Test error")

    provider = PlexProvider("test_token")
    result = provider.get_watchlist()

    assert result == []


def test_get_watchlist_empty(mock_plex_account):
    mock_plex_account.return_value.watchlist.return_value = []

    provider = PlexProvider("test_token")
    result = provider.get_watchlist()

    assert result == []
