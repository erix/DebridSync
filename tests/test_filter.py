import unittest
from src.models.filter import Filter
from src.models.release import Release


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.filter = Filter(resolutions=["2160p", "1080p", "720p"])
        self.releases = [
            Release(
                title="Movie 2160p HDR", infoHash="hash1", size_in_gb=20.0, peers=10
            ),
            Release(
                title="Movie 1080p HDR", infoHash="hash2", size_in_gb=10.0, peers=20
            ),
            Release(title="Movie 1080p", infoHash="hash3", size_in_gb=8.0, peers=15),
            Release(title="Movie 720p", infoHash="hash4", size_in_gb=5.0, peers=25),
        ]

    def test_apply_filter_highest_resolution(self):
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 1)
        self.assertEqual(filtered_releases[0].title, "Movie 2160p HDR")

    def test_apply_filter_largest_size(self):
        self.releases.append(
            Release(
                title="Movie 2160p HDR Large",
                infoHash="hash5",
                size_in_gb=30.0,
                peers=5,
            )
        )
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 1)
        self.assertEqual(filtered_releases[0].title, "Movie 2160p HDR Large")

    def test_apply_filter_without_hdr(self):
        self.filter.preferred_dynamic_range = None
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 1)
        self.assertEqual(filtered_releases[0].title, "Movie 2160p HDR")

    def test_apply_filter_with_hdr(self):
        self.releases = [
            Release(
                title="Movie 2160p HDR", infoHash="hash1", size_in_gb=20.0, peers=10
            ),
            Release(
                title="Movie 1080p HDR", infoHash="hash2", size_in_gb=10.0, peers=20
            ),
            Release(title="Movie 1080p", infoHash="hash3", size_in_gb=8.0, peers=15),
        ]
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 1)
        self.assertEqual(filtered_releases[0].title, "Movie 2160p HDR")
        self.assertEqual(filtered_releases[0].size_in_gb, 20.0)
        self.assertEqual(filtered_releases[0].peers, 10)

    def test_apply_filter_only_1080p(self):
        self.filter.resolutions = ["1080p"]
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 1)
        self.assertEqual(filtered_releases[0].title, "Movie 1080p HDR")

    def test_apply_filter_fallback_to_lower_resolution(self):
        self.releases = [
            Release(title="Movie 1080p", infoHash="hash3", size_in_gb=8.0, peers=15),
            Release(title="Movie 720p", infoHash="hash4", size_in_gb=5.0, peers=25),
        ]
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 1)
        self.assertEqual(filtered_releases[0].title, "Movie 1080p")

    def test_apply_filter_no_matching_releases(self):
        self.releases = [
            Release(title="Movie 480p", infoHash="hash5", size_in_gb=2.0, peers=30),
        ]
        filtered_releases = self.filter.apply(self.releases)
        self.assertEqual(len(filtered_releases), 0)


if __name__ == "__main__":
    unittest.main()
