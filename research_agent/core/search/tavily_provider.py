from typing import List, Dict, Any
from tavily import TavilyClient
from research_agent.core.search.base import BaseSearchProvider
from research_agent.config.settings import settings

class TavilySearchProvider(BaseSearchProvider):
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def search(self, query: str) -> List[Dict[str, Any]]:
        response = self.client.search(query, search_depth="advanced")
        results = []
        for result in response.get("results", []):
            results.append({
                "title": result.get("title"),
                "url": result.get("url"),
                "content": result.get("content")
            })
        return results
