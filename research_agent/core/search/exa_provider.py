import requests
from typing import List, Dict, Any
from research_agent.core.search.base import BaseSearchProvider
from research_agent.config.settings import settings

class ExaSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.EXA_API_KEY
        self.base_url = "https://api.exa.ai/search"
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a search using Exa Deep Research API.
        """
        if not self.api_key:
            raise ValueError("EXA_API_KEY is not set. Please add it to your .env file.")
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Using Deep Research mode
        payload = {
            'query': query,
            'useAutoprompt': True,
            'type': 'deep',
            'numResults': 15,
            'contents': {
                'text': True,
                'summary': True
            }
        }
        
        try:
            print(f"Exa Provider: Performing Deep Research for '{query}'...")
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('results', []):
                results.append({
                    'title': item.get('title', 'No Title'),
                    'url': item.get('url', ''),
                    'content': item.get('text', item.get('summary', ''))
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Exa API Error: {e}")
            return []
