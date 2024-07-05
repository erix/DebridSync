from abc import ABC, abstractmethod
from typing import List, Dict

class ContentProvider(ABC):
    @abstractmethod
    def get_watchlist(self) -> List[Dict[str, str]]:
        pass
