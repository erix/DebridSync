from abc import ABC, abstractmethod
from typing import List, Dict, Any


class MediaCollectionProvider(ABC):
    @abstractmethod
    def get_watchlist(self) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def remove_from_watchlist(self, item: Dict[str, str]) -> bool:
        pass

    @abstractmethod
    def get_user_collection(self) -> List[Dict[str, str]]:
        pass
