import json
from typing import List, Dict
from research_agent.core.llm.base import BaseLLMProvider
from research_agent.core.search.serper_provider import SerperProvider
from research_agent.core.search.exa_provider import ExaSearchProvider
from research_agent.core.llm.factory import get_llm_provider
from research_agent.config.settings import settings

class CollectorAgent:
    def __init__(self, use_deep_research: bool = False):
        self.llm: BaseLLMProvider = get_llm_provider()
        self.use_deep_research = use_deep_research
        
        if use_deep_research:
            self.search_tool = ExaSearchProvider()
        elif settings.DEFAULT_SEARCH_PROVIDER == "mock":
            from research_agent.core.search.mock_provider import MockSearchProvider
            self.search_tool = MockSearchProvider()
        elif settings.DEFAULT_SEARCH_PROVIDER == "tavily":
            from research_agent.core.search.tavily_provider import TavilySearchProvider
            self.search_tool = TavilySearchProvider()
        else:
            self.search_tool = SerperProvider()

    def collect(self, query: str, history: List[Dict] = [], status_callback=None) -> Dict:
        """
        Collect information about the query.
        Returns a dictionary with collected context and sources.
        """
        if status_callback:
            status_callback(f"Collector Agent: Analyzing query '{query}'...")
        else:
            print(f"Collector Agent: Analyzing query '{query}'...")

        # Step 1: Handle Deep Research (Exa) vs Standard Search
        if self.use_deep_research:
            if status_callback:
                status_callback("Exa Deep Research: Performing autonomous web exploration...")
            print(f"Exa Deep Research: Performing autonomous web exploration for '{query}'...")
            
            try:
                # Exa handles its own multi-query/depth logic
                results = self.search_tool.search(query)
                collected_data = []
                sources = []
                documents = []
                
                for result in results:
                    collected_data.append(f"Source: {result['title']} ({result['url']})\nContent: {result['content']}")
                    sources.append({"title": result['title'], "url": result['url']})
                    if result['url'].lower().endswith(('.pdf', '.docx', '.xlsx')):
                         documents.append({"title": result['title'], "url": result['url'], "type": result['url'].split('.')[-1]})
                
                return {
                    "context": "\n\n".join(collected_data),
                    "sources": sources,
                    "documents": documents
                }
            except Exception as e:
                print(f"DEBUG: Exa Deep Research Failed: {e}. Falling back to standard search.")
                if status_callback:
                    status_callback("Exa failed. Falling back to standard search...")

        # Standard Search Logic (Serper/Tavily)
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
        
        if status_callback:
            status_callback("Planning search strategy...")
        print("DEBUG: Calling LLM for search plan...")
        try:
            response = self.llm.generate(plan_prompt, history=history, system_prompt="You are a helpful assistant. Output only JSON.")
            print("DEBUG: LLM plan generated successfully.")
        except Exception as e:
            print(f"DEBUG: LLM Planning Failed: {e}")
            # Fallback plan
            response = json.dumps({"search_queries": [query], "look_for_documents": False})
        
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
            if status_callback:
                status_callback(f"Searching for: {q}...")
            print(f"Collector Agent: Searching for '{q}'...")
            try:
                results = self.search_tool.search(q)
            except Exception as e:
                print(f"DEBUG: Search Failed for '{q}': {e}")
                continue
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
            
            if status_callback:
                status_callback("Aggressively searching for documents...")
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
