from abc import ABC, abstractmethod
from typing import List


class IPersistenceProvider(ABC):
    @abstractmethod
    def save_many(self, headers: List[str], data: List[dict]):
        pass
