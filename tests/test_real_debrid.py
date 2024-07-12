import pytest
from unittest.mock import patch, MagicMock
from src.debrid.real_debrid import RealDebrid

@pytest.fixture
def real_debrid():
    return RealDebrid("test_api_token")

@pytest.fixture
def mock_requests():
    with patch('src.debrid.real_debrid.requests') as mock:
        yield mock

def test_add_torrent(real_debrid, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "test_torrent_id"}
    mock_requests.post.return_value = mock_response

    result = real_debrid.add_torrent("test_hash")

    assert result == {"id": "test_torrent_id"}
    mock_requests.post.assert_called_once_with(
        "https://api.real-debrid.com/rest/1.0/torrents/addMagnet",
        headers=real_debrid.headers,
        data={"magnet": "magnet:?xt=urn:btih:test_hash"}
    )

def test_select_files(real_debrid, mock_requests):
    mock_response = MagicMock()
    mock_requests.post.return_value = mock_response

    real_debrid.select_files("test_torrent_id")

    mock_requests.post.assert_called_once_with(
        "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/test_torrent_id",
        headers=real_debrid.headers,
        data={"files": "all"}
    )

def test_get_torrent_info(real_debrid, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "downloaded"}
    mock_requests.get.return_value = mock_response

    result = real_debrid.get_torrent_info("test_torrent_id")

    assert result == {"status": "downloaded"}
    mock_requests.get.assert_called_once_with(
        "https://api.real-debrid.com/rest/1.0/torrents/info/test_torrent_id",
        headers=real_debrid.headers
    )

def test_get_user_torrents(real_debrid, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "torrent1"}, {"id": "torrent2"}]
    mock_response.headers = {"X-Total-Count": "2"}
    mock_requests.get.return_value = mock_response

    result = real_debrid.get_user_torrents()

    assert result == [{"id": "torrent1"}, {"id": "torrent2"}]
    mock_requests.get.assert_called_once_with(
        "https://api.real-debrid.com/rest/1.0/torrents",
        headers=real_debrid.headers,
        params={"limit": 100, "offset": 0}
    )

def test_get_user_torrents_multiple_pages(real_debrid, mock_requests):
    mock_responses = [
        MagicMock(json=lambda: [{"id": f"torrent{i}"} for i in range(1, 101)], headers={"X-Total-Count": "150"}),
        MagicMock(json=lambda: [{"id": f"torrent{i}"} for i in range(101, 151)], headers={"X-Total-Count": "150"})
    ]
    mock_requests.get.side_effect = mock_responses

    result = real_debrid.get_user_torrents()

    assert len(result) == 150
    assert result[0] == {"id": "torrent1"}
    assert result[-1] == {"id": "torrent150"}
    assert mock_requests.get.call_count == 2
