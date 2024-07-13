import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List
from datetime import datetime
from unittest.mock import patch

from content.content_manager import ContentManager, ContentProvider
from content.trakt_provider import TraktProvider
from models.movie import Movie, MediaType


class MockProvider(ContentProvider):
    def get_watchlist(self) -> List[Dict[str, str]]:
        return [
            {"title": "Test Movie 1", "year": "2023"},
            {"title": "Test Movie 2", "year": "2022"},
        ]

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
    assert watchlist == [
        {"title": "Test Movie 1", "year": "2023"},
        {"title": "Test Movie 2", "year": "2022"},
    ]


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
        "Test1": [
            {"title": "Test Movie 1", "year": "2023"},
            {"title": "Test Movie 2", "year": "2022"},
        ],
        "Test2": [
            {"title": "Test Movie 1", "year": "2023"},
            {"title": "Test Movie 2", "year": "2022"},
        ],
    }

@pytest.fixture
def mock_trakt():
    with patch("content.trakt_provider.trakt.Trakt") as mock:
        yield mock

def test_check_released_true(mock_trakt):
    provider = TraktProvider("test_id", "test_secret")
    mock_movie = MagicMock()
    mock_movie.released = "2023-01-01"
    mock_trakt["movies"].get.return_value = mock_movie

    movie = Movie(title="Test Movie", year="2023", imdb_id="tt1234567", media_type=MediaType.MOVIE)
    result = provider.check_released(movie)

    assert result is True
    mock_trakt["movies"].get.assert_called_once_with("tt1234567")

def test_check_released_false(mock_trakt):
    provider = TraktProvider("test_id", "test_secret")
    mock_movie = MagicMock()
    mock_movie.released = "2024-01-01"  # Future date
    mock_trakt["movies"].get.return_value = mock_movie

    movie = Movie(title="Test Movie", year="2023", imdb_id="tt1234567", media_type=MediaType.MOVIE)
    
    with patch('content.trakt_provider.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 6, 1)  # Set current date to June 1, 2023
        result = provider.check_released(movie)

    assert result is False
    mock_trakt["movies"].get.assert_called_once_with("tt1234567")

def test_check_released_no_date(mock_trakt):
    provider = TraktProvider("test_id", "test_secret")
    mock_movie = MagicMock()
    mock_movie.released = None
    mock_trakt["movies"].get.return_value = mock_movie

    movie = Movie(title="Test Movie", year="2023", imdb_id="tt1234567", media_type=MediaType.MOVIE)
    result = provider.check_released(movie)

    assert result is False
    mock_trakt["movies"].get.assert_called_once_with("tt1234567")

def test_check_released_error(mock_trakt):
    provider = TraktProvider("test_id", "test_secret")
    mock_trakt["movies"].get.side_effect = Exception("API Error")

    movie = Movie(title="Test Movie", year="2023", imdb_id="tt1234567", media_type=MediaType.MOVIE)
    result = provider.check_released(movie)

    assert result is False
    mock_trakt["movies"].get.assert_called_once_with("tt1234567")
