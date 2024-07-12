import unittest
from unittest.mock import Mock
from src.indexer.indexer_manager import IndexerManager, Indexer
from src.models.release import Release


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
        with self.assertRaises(ValueError):
            self.manager.get_indexer("non_existent_indexer")

    def test_find_releases(self):
        mock_indexer = Mock(spec=Indexer)
        mock_indexer.find_releases.return_value = [
            Release(title="Test Release", infoHash="123456", size_in_gb=1.5, peers=10)
        ]
        self.manager.add_indexer("test_indexer", mock_indexer)

        results = self.manager.find_releases(
            "test_indexer", "tt1234567", "movie", "Test Movie"
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Test Release")
        self.assertEqual(results[0].infoHash, "123456")
        self.assertEqual(results[0].size_in_gb, 1.5)
        self.assertEqual(results[0].peers, 10)
        mock_indexer.find_releases.assert_called_once_with(
            "tt1234567", "movie", "Test Movie"
        )

    def test_find_releases_invalid_indexer(self):
        with self.assertRaises(ValueError):
            self.manager.find_releases(
                "non_existent_indexer", "tt1234567", "movie", "Test Movie"
            )


if __name__ == "__main__":
    unittest.main()
