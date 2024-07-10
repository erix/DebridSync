from RTN import SettingsModel
from RTN.models import BaseRankingModel


class TorrentSettings(SettingsModel):
    def __init__(self):
        super().__init__(
            require=["1080p", "4K"],
            exclude=["CAM", "TS"],
            preferred=["HDR", "BluRay"],
        )


class MyRankingModel(BaseRankingModel):
    uhd: int = 200  # Ultra HD content
    hdr: int = 100  # HDR content
    # Define more attributes and scores as needed
