import unittest
from unittest.mock import patch, Mock
from src.release_finder.torrentio_finder import Torrentio

class TestTorrentio(unittest.TestCase):
    def setUp(self):
        self.torrentio = Torrentio()

    @patch('src.release_finder.torrentio_finder.requests.get')
    def test_find_releases_movie(self, mock_get):
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "streams": [
                {
                    "name": "Torrentio\n4k DV | HDR10+",
                    "title": "Movie.Title.2024.2160p.DV.HDR10Plus.HEVC.DDP5.1.Atmos",
                    "infoHash": "1234567890abcdef1234567890abcdef12345678"
                },
                {
                    "name": "Torrentio\n1080p",
                    "title": "Movie.Title.2024.1080p.WEB-DL.x264",
                    "infoHash": "abcdef1234567890abcdef1234567890abcdef12"
                }
            ]
        }
        mock_get.return_value = mock_response

        # Test the find_releases method
        releases = self.torrentio.find_releases("tt1234567", "movie")

        # Assert the results
        self.assertEqual(len(releases), 2)
        self.assertEqual(releases[0]["title"], "Movie.Title.2024.2160p.DV.HDR10Plus.HEVC.DDP5.1.Atmos")
        self.assertEqual(releases[0]["infoHash"], "1234567890abcdef1234567890abcdef12345678")
        self.assertEqual(releases[1]["title"], "Movie.Title.2024.1080p.WEB-DL.x264")
        self.assertEqual(releases[1]["infoHash"], "abcdef1234567890abcdef1234567890abcdef12")

        # Assert that the correct URL was called
        mock_get.assert_called_once_with(
            "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/stream/movie/tt1234567.json"
        )

    @patch('src.release_finder.torrentio_finder.requests.get')
    def test_find_releases_show(self, mock_get):
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "streams": [
                {
                    "name": "Torrentio\n1080p",
                    "title": "TV.Show.S01E01.1080p.WEB-DL.x264",
                    "infoHash": "0123456789abcdef0123456789abcdef01234567"
                }
            ]
        }
        mock_get.return_value = mock_response

        # Test the find_releases method
        releases = self.torrentio.find_releases("tt9876543", "show")

        # Assert the results
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0]["title"], "TV.Show.S01E01.1080p.WEB-DL.x264")
        self.assertEqual(releases[0]["infoHash"], "0123456789abcdef0123456789abcdef01234567")

        # Assert that the correct URL was called
        mock_get.assert_called_once_with(
            "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/stream/show/tt9876543.json"
        )

    @patch('src.release_finder.torrentio_finder.requests.get')
    def test_find_releases_no_results(self, mock_get):
        # Mock an empty API response
        mock_response = Mock()
        mock_response.json.return_value = {"streams": []}
        mock_get.return_value = mock_response

        # Test the find_releases method
        releases = self.torrentio.find_releases("tt0000000", "movie")

        # Assert that an empty list is returned
        self.assertEqual(releases, [])

    def test_find_releases_invalid_media_type(self):
        # Test with an invalid media type
        with self.assertRaises(ValueError):
            self.torrentio.find_releases("tt1234567", "invalid_type")

if __name__ == '__main__':
    unittest.main()
