from abc import ABC, abstractmethod
from typing import List

class ContentProvider(ABC):
    @abstractmethod
    def get_watchlist(self) -> List[str]:
        pass

