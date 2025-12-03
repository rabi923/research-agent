import json
from typing import List, Dict
from research_agent.core.llm.base import BaseLLMProvider
from research_agent.core.search.tavily_provider import TavilySearchProvider
from research_agent.core.llm.factory import get_llm_provider
from research_agent.config.settings import settings

class CollectorAgent:
    def __init__(self):
        self.llm: BaseLLMProvider = get_llm_provider()
        if settings.DEFAULT_SEARCH_PROVIDER == "mock":
            from research_agent.core.search.mock_provider import MockSearchProvider
            self.search_tool = MockSearchProvider()
        else:
            self.search_tool = TavilySearchProvider()

    def collect(self, query: str, history: List[Dict] = []) -> Dict:
        """
        Collect information about the query.
        Returns a dictionary with collected context and sources.
        """
        print(f"Collector Agent: Analyzing query '{query}'...")

        # Step 1: Generate search queries
        plan_prompt = f"""
        You are an expert Information Collector. Your goal is to gather comprehensive information about the user's query.
        Analyze the query and generate 3-5 distinct search queries to cover different aspects of the topic.
        Also, identify if we should specifically look for documents (PDF, DOCX, XLSX).

        User Query: {query}

        Return a JSON object with:
        - "search_queries": list of strings
        - "look_for_documents": boolean (true if the query implies need for papers, reports, data sheets)
        """
        
        response = self.llm.generate(plan_prompt, history=history, system_prompt="You are a helpful assistant. Output only JSON.")
        
        try:
            response = response.replace("```json", "").replace("```", "").strip()
            plan = json.loads(response)
            search_queries = plan.get("search_queries", [query])
            look_for_documents = plan.get("look_for_documents", False)
        except json.JSONDecodeError:
            search_queries = [query]
            look_for_documents = False

        collected_data = []
        sources = []
        documents = []

        # Step 2: Execute searches
        for q in search_queries:
            print(f"Collector Agent: Searching for '{q}'...")
            results = self.search_tool.search(q)
            for result in results:
                collected_data.append(f"Source: {result['title']} ({result['url']})\nContent: {result['content']}")
                sources.append({"title": result['title'], "url": result['url']})
                
                # Check for documents
                if result['url'].lower().endswith(('.pdf', '.docx', '.xlsx')):
                     documents.append({"title": result['title'], "url": result['url'], "type": result['url'].split('.')[-1]})

        # Step 3: Optional document specific search
        # Always check for documents if the query implies research
        if look_for_documents or True: # Force document search for deep research
            # Aggressive search for multiple file types
            doc_queries = [
                f"{query} filetype:pdf",
                f"{query} filetype:docx",
                f"{query} filetype:xlsx"
            ]
            
            print(f"Collector Agent: Aggressively searching for documents...")
            for doc_query in doc_queries:
                print(f"  - Searching: '{doc_query}'")
                doc_results = self.search_tool.search(doc_query)
                for result in doc_results:
                     ext = result['url'].split('.')[-1].lower()
                     if ext in ['pdf', 'docx', 'xlsx']:
                         # Avoid duplicates
                         if not any(d['url'] == result['url'] for d in documents):
                             documents.append({"title": result['title'], "url": result['url'], "type": ext})
                             collected_data.append(f"Document Found: {result['title']} ({result['url']})\nContent: {result['content']}")

        return {
            "context": "\n\n".join(collected_data),
            "sources": sources,
            "documents": documents
        }
