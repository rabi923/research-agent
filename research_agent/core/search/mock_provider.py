from typing import List, Dict, Any
from research_agent.core.search.base import BaseSearchProvider

class MockSearchProvider(BaseSearchProvider):
    def search(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Mock Search Result 1",
                "url": "http://mock.url/1",
                "content": f"This is a mock search result content for query: {query}"
            },
            {
                "title": "Mock Search Result 2",
                "url": "http://mock.url/2",
                "content": "Another mock result with some interesting information."
            }
        ]
