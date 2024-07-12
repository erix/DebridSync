import unittest
from unittest.mock import Mock
from src.indexer.indexer_manager import IndexerManager
from src.indexer.indexer import Indexer


class TestIndexerManager(unittest.TestCase):
    def setUp(self):
        self.manager = IndexerManager()

    def test_add_indexer(self):
        mock_indexer = Mock(spec=Indexer)
        self.manager.add_indexer("test_indexer", mock_indexer)
        self.assertIn("test_indexer", self.manager.indexers)
        self.assertEqual(self.manager.indexers["test_indexer"], mock_indexer)

    def test_get_indexer(self):
        mock_indexer = Mock(spec=Indexer)
        self.manager.add_indexer("test_indexer", mock_indexer)
        retrieved_indexer = self.manager.get_indexer("test_indexer")
        self.assertEqual(retrieved_indexer, mock_indexer)

    def test_get_indexer_not_found(self):
        with self.assertRaises(ValueError):  # Changed from ValueError to KeyError
            self.manager.get_indexer("non_existent_indexer")

    def test_find_releases(self):
        mock_indexer = Mock(spec=Indexer)
        mock_indexer.find_releases.return_value = [
            {"title": "Test Release", "infoHash": "123456"}
        ]
        self.manager.add_indexer("test_indexer", mock_indexer)

        results = self.manager.find_releases("test_indexer", "tt1234567", "movie", "Test Movie")
        self.assertEqual(results, [{"title": "Test Release", "infoHash": "123456"}])
        mock_indexer.find_releases.assert_called_once_with("tt1234567", "movie", "Test Movie")

    def test_find_releases_invalid_indexer(self):
        with self.assertRaises(ValueError):
            self.manager.find_releases("non_existent_indexer", "tt1234567", "movie", "Test Movie")


if __name__ == "__main__":
    unittest.main()
