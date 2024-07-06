from dataclasses import dataclass, field
from typing import List

from icecream import ic


@dataclass
class QualityProfile:
    resolutions: List[str]

    def apply(self, releases):
        for resolution in self.resolutions:
            resolution_filtered = [
                release
                for release in releases
                if resolution.lower() in release.title.lower()
            ]
            ic(resolution, resolution_filtered)
            if resolution_filtered:
                # Sort by size_in_gb (descending) and then by peers (descending)
                return [max(resolution_filtered, key=lambda r: (r.size_in_gb, r.peers))]
        return []
