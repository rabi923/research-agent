import json
from typing import Optional
from research_agent.core.llm.factory import get_llm_provider
from research_agent.core.tts.factory import get_tts_provider
from research_agent.config.settings import settings
from research_agent.agent.collector import CollectorAgent
from research_agent.agent.analyzer import AnalyzerAgent

class ResearchAgent:
    def __init__(self, use_deep_research: bool = False):
        self.collector = CollectorAgent(use_deep_research=use_deep_research)
        self.analyzer = AnalyzerAgent()
        self.tts_tool = get_tts_provider()
        self.last_collected_data = None
        self.last_query = None
        self.use_deep_research = use_deep_research
        print(f"DEBUG: Active TTS Provider: {self.tts_tool.__class__.__name__}")
        print(f"DEBUG: Deep Research Mode: {use_deep_research}")

    def process_query(self, query: str, history: list[dict] = [], status_callback=None, use_deep_research: Optional[bool] = None) -> dict:
        """
        Process a user query:
        1. Classify: Chat or Research?
        2. If Chat: Respond directly.
        3. If Research: Collect, Analyze, Speak.
        """
        
        # ... (Classification logic remains the same) ...
        
        # Step 1: Classify
        classify_prompt = f"""
        You are a smart AI assistant should sound like FRIDAY for ironman and your name is FRIDAY. Your job is to strictly categorize the user's input into one of two categories:
        
        1. "CHAT": Casual conversation, greetings, compliments, personal questions about you (the AI), or simple requests that do NOT require external information.
           Examples: "Hi", "Hello", "How are you?", "Who are you?", "Good morning", "Thanks", "Write a poem about love".
           
        2. "RESEARCH": Questions that require factual information, data, news, or knowledge from the internet.
           ALSO include requests to generate documents (PDF, Word, Excel) from previous topics.
           Examples: "Who is the CEO of Google?", "Cricket Score", "Latest stock price of Apple", "Explain quantum computing", "History of Rome", "Weather in London", "Make it a word doc", "Save as PDF".
        
        User Query: "{query}"
        
        Return a JSON object with:
        - "type": "CHAT" or "RESEARCH"
        - "response": string (if CHAT, provide a friendly, natural response here. If RESEARCH, return null)
        """
        
        try:
            classify_response = self.collector.llm.generate(classify_prompt, history=history, system_prompt="You are a helpful assistant. Output only JSON.")
            classify_response = classify_response.replace("```json", "").replace("```", "").strip()
            classification = json.loads(classify_response)
        except Exception:
            # Fallback to research if classification fails
            classification = {"type": "RESEARCH"}

        if classification.get("type") == "CHAT":
            answer = classification.get("response", "Hello! How can I help you today?")
            audio_bytes = self.tts_tool.speak(answer)
            return {
                "answer": answer,
                "audio": audio_bytes,
                "sources": [],
                "documents": [],
                "pdf_path": None
            }

        # Step 2: Determine if this is a formatting request for previous data
        # We check if the query implies formatting AND we have previous data
        is_formatting_request = False
        query_lower = query.lower()
        formatting_keywords = ["word", "docx", "pdf", "excel", "spreadsheet", "csv", "document", "file"]
        if self.last_collected_data and any(k in query_lower for k in formatting_keywords):
            # Simple heuristic: if asking for format and we have data, assume it's for that data
            # Ideally we'd ask LLM to confirm, but this is faster/cheaper.
            # Let's assume if it's short and contains format keywords, it's a reformat.
            if len(query.split()) < 10: 
                is_formatting_request = True

        collected_data = None
        
        if is_formatting_request:
            if status_callback:
                status_callback("Reuse previous research data...")
            print("DEBUG: Reusing previous collected data...")
            collected_data = self.last_collected_data
            # Use the previous query title for the file name, or the current query if it makes sense
            # We'll stick to the current query for the report title to reflect the user's new intent
        else:
            # Step 2: Collect (Research Mode)
            if status_callback:
                status_callback("Starting Collection Phase...")
            print("Starting Collection Phase...")
            
            # If a one-off flag is passed, update collector
            if use_deep_research is not None:
                self.collector.use_deep_research = use_deep_research
                if use_deep_research:
                    from research_agent.core.search.exa_provider import ExaSearchProvider
                    self.collector.search_tool = ExaSearchProvider()
                else:
                    from research_agent.core.search.serper_provider import SerperProvider
                    self.collector.search_tool = SerperProvider()

            collected_data = self.collector.collect(query, history, status_callback=status_callback)
            
            # Update state
            self.last_collected_data = collected_data
            self.last_query = query
        
        # Determine requested formats
        requested_formats = ["pdf"] # Default
        if "word" in query_lower or "docx" in query_lower:
            requested_formats.append("docx")
        if "excel" in query_lower or "spreadsheet" in query_lower or "csv" in query_lower:
            requested_formats.append("excel")

        # Step 3: Analyze
        if status_callback:
            status_callback(f"Starting Analysis Phase (Formats: {requested_formats})...")
        print(f"Starting Analysis Phase (Formats: {requested_formats})...")
        
        # If reusing data, we might want to pass the ORIGINAL query to the analyzer so the report stays focused,
        # but the user might have asked "Summarize it better", so we pass the current query.
        # However, for file generation "Make it a word doc", the query is just that.
        # The analyzer prompt uses the query. If query is "Make it a word doc", the report might be weird.
        # Better to use last_query if it's a formatting request.
        analysis_query = self.last_query if is_formatting_request else query
        
        analysis_result = self.analyzer.analyze(analysis_query, collected_data, history, requested_formats=requested_formats, status_callback=status_callback)
        
        report_content = analysis_result["report_content"]
        pdf_path = analysis_result["pdf_path"]
        sources = analysis_result["sources"]
        documents = analysis_result["documents"]

        # Step 4: Speak (Summary)
        # We'll ask the LLM to generate a brief spoken summary of the report
        summary_prompt = f"""
        Based on the following report, generate a concise, conversational summary suitable for speech (1-2 sentences).
        
        Report:
        {report_content}
        """
        # We can use the collector's LLM for this simple task
        if status_callback:
            status_callback("Generating spoken summary...")
        print("DEBUG: Generating summary...")
        try:
            summary = self.collector.llm.generate(summary_prompt, history=history, system_prompt="You are a helpful assistant. Be concise.")
            print(f"DEBUG: Summary generated: {summary[:50]}...")
        except Exception as e:
            print(f"DEBUG: Summary Generation Failed: {e}")
            summary = "Here is your report."

        if status_callback:
            status_callback("Generating audio response...")
        print("DEBUG: Generating audio...")
        try:
            audio_bytes = self.tts_tool.speak(summary)
            print("DEBUG: Audio generated successfully.")
        except Exception as e:
            print(f"DEBUG: Audio Generation Failed: {e}")
            audio_bytes = None

        return {
            "answer": report_content,
            "audio": audio_bytes,
            "sources": sources,
            "documents": documents,
            "pdf_path": pdf_path,
            "docx_path": analysis_result.get("docx_path"),
            "excel_path": analysis_result.get("excel_path")
        }
