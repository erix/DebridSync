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
    mock_item.year = "2023"
    mock_item.get_key.return_value = "tt1234567"
    mock_trakt.__getitem__.return_value.get.return_value = [mock_item]

    provider = TraktProvider("test_id", "test_secret")
    with patch.object(provider, '_get_media_type', return_value='show'):
        result = provider.get_watchlist()

    assert result == [{
        'title': "Test Show",
        'year': "2023",
        'imdb_id': "tt1234567",
        'media_type': 'show'
    }]

def test_get_watchlist_failure(mock_trakt):
    mock_trakt.__getitem__.return_value.get.side_effect = Exception("Test error")

    provider = TraktProvider("test_id", "test_secret")
    result = provider.get_watchlist()

    assert result == []

@pytest.mark.skip
def test_get_media_type():
    provider = TraktProvider("test_id", "test_secret")
    
    movie_item = MagicMock()
    movie_item.__class__.__name__ = 'Movie'
    assert provider._get_media_type(movie_item) == 'movie'
    
    show_item = MagicMock()
    show_item.__class__.__name__ = 'Show'
    assert provider._get_media_type(show_item) == 'show'
    
    unknown_item = MagicMock()
    unknown_item.__class__.__name__ = 'Unknown'
    assert provider._get_media_type(unknown_item) == 'unknown'

    episode_item = MagicMock()
    episode_item.__class__.__name__ = 'Episode'
    assert provider._get_media_type(episode_item) == 'episode'

    season_item = MagicMock()
    season_item.__class__.__name__ = 'Season'
    assert provider._get_media_type(season_item) == 'show'
