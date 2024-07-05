import unittest
from unittest.mock import Mock
from src.release_finder.release_finder_manager import ReleaseFinderManager
from src.release_finder.release_finder import ReleaseFinder

class TestReleaseFinderManager(unittest.TestCase):
    def setUp(self):
        self.manager = ReleaseFinderManager()

    def test_add_finder(self):
        mock_finder = Mock(spec=ReleaseFinder)
        self.manager.add_finder("test_finder", mock_finder)
        self.assertIn("test_finder", self.manager.finders)
        self.assertEqual(self.manager.finders["test_finder"], mock_finder)

    def test_get_finder(self):
        mock_finder = Mock(spec=ReleaseFinder)
        self.manager.add_finder("test_finder", mock_finder)
        retrieved_finder = self.manager.get_finder("test_finder")
        self.assertEqual(retrieved_finder, mock_finder)

    def test_get_finder_not_found(self):
        with self.assertRaises(ValueError):  # Changed from ValueError to KeyError
            self.manager.get_finder("non_existent_finder")

    def test_find_releases(self):
        mock_finder = Mock(spec=ReleaseFinder)
        mock_finder.find_releases.return_value = [{"title": "Test Release", "infoHash": "123456"}]
        self.manager.add_finder("test_finder", mock_finder)

        results = self.manager.find_releases("test_finder", "tt1234567", "movie")
        self.assertEqual(results, [{"title": "Test Release", "infoHash": "123456"}])
        mock_finder.find_releases.assert_called_once_with("tt1234567", "movie")

    def test_find_releases_invalid_finder(self):
        with self.assertRaises(ValueError):  # Changed from ValueError to KeyError
            self.manager.find_releases("non_existent_finder", "tt1234567", "movie")

if __name__ == '__main__':
    unittest.main()
