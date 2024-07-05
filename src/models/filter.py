from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Filter:
    resolutions: List[str] = field(default_factory=lambda: ['2160p', '1080p'])
    preferred_dynamic_range: Optional[str] = None

    def apply(self, releases):
        filtered_releases = []
        for release in releases:
            if any(res.lower() in release.title.lower() for res in self.resolutions):
                if self.preferred_dynamic_range:
                    if self.preferred_dynamic_range.lower() in release.title.lower():
                        filtered_releases.append(release)
                else:
                    filtered_releases.append(release)
        return filtered_releases
