import unittest
from src.models.filter import Filter
from src.models.release import Release

class TestFilter(unittest.TestCase):
    def setUp(self):
        self.filter = Filter(min_resolution='1080p', preferred_dynamic_range='HDR')
        self.releases = [
            Release(title="Movie 2160p HDR", infoHash="hash1", size_in_gb=20.0, peers=10),
            Release(title="Movie 1080p HDR", infoHash="hash2", size_in_gb=10.0, peers=20),
            Release(title="Movie 1080p", infoHash="hash3", size_in_gb=8.0, peers=15),
            Release(title="Movie 720p", infoHash="hash4", size_in_gb=5.0, peers=25),
        ]

    def test_apply_filter(self):
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 2)
        self.assertEqual(filtered_releases[0].title, "Movie 2160p HDR")
        self.assertEqual(filtered_releases[1].title, "Movie 1080p HDR")

    def test_apply_filter_without_hdr(self):
        self.filter.preferred_dynamic_range = None
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 3)
        self.assertEqual(filtered_releases[0].title, "Movie 2160p HDR")
        self.assertEqual(filtered_releases[1].title, "Movie 1080p HDR")
        self.assertEqual(filtered_releases[2].title, "Movie 1080p")

    def test_apply_filter_lower_resolution(self):
        self.filter.min_resolution = '720p'
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 2)
        self.assertEqual(filtered_releases[0].title, "Movie 2160p HDR")
        self.assertEqual(filtered_releases[1].title, "Movie 1080p HDR")

if __name__ == '__main__':
    unittest.main()
