import requests
from typing import List, Dict, Any
from research_agent.core.search.base import BaseSearchProvider
from research_agent.config.settings import settings

class SerperProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a search using Serper.dev API.
        Returns a list of results with 'title', 'url', and 'content'.
        """
        if not self.api_key:
            raise ValueError("SERPER_API_KEY is not set. Please add it to your .env file or Streamlit Secrets.")
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': 10  # Number of results
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Process organic results
            if 'organic' in data:
                for item in data['organic']:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'content': item.get('snippet', '')
                    })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Serper API Error: {e}")
            return []
