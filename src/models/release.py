from dataclasses import dataclass

@dataclass
class Release:
    title: str
    infoHash: str
    size_in_gb: float
    peers: int
