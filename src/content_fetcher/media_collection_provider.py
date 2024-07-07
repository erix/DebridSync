from abc import ABC, abstractmethod
from typing import List, Dict


class MediaCollectionProvider(ABC):
    @abstractmethod
    def get_user_collection(self) -> List[Dict[str, str]]:
        pass
