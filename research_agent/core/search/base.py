from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSearchProvider(ABC):
    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a search and return a list of results.
        Each result should be a dict with 'title', 'url', and 'content'.
        """
        pass
