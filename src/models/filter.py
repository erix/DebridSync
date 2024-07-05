from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Filter:
    min_resolution: str = '720p'
    preferred_dynamic_range: Optional[str] = None
    resolution_order: List[str] = ('2160p', '1080p', '720p')

    def apply(self, releases):
        filtered_releases = []
        for release in releases:
            resolution = next((res for res in self.resolution_order if res in release.title.lower()), None)
            if resolution and self.resolution_order.index(resolution) <= self.resolution_order.index(self.min_resolution):
                if self.preferred_dynamic_range:
                    if self.preferred_dynamic_range.lower() in release.title.lower():
                        filtered_releases.append(release)
                else:
                    filtered_releases.append(release)
        return filtered_releases
