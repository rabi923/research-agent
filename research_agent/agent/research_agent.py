import json
from typing import Optional
from research_agent.core.llm.factory import get_llm_provider
from research_agent.core.tts.factory import get_tts_provider
from research_agent.config.settings import settings
from research_agent.agent.collector import CollectorAgent
from research_agent.agent.analyzer import AnalyzerAgent

class ResearchAgent:
    def __init__(self):
        self.collector = CollectorAgent()
        self.analyzer = AnalyzerAgent()
        self.tts_tool = get_tts_provider()

    def process_query(self, query: str, history: list[dict] = []) -> dict:
        """
        Process a user query:
        1. Classify: Chat or Research?
        2. If Chat: Respond directly.
        3. If Research: Collect, Analyze, Speak.
        """
        
        # Step 1: Classify
        classify_prompt = f"""
        You are a helpful assistant. Determine if the following user query requires a web search (RESEARCH) or if it's a casual conversation/greeting (CHAT).
        
        User Query: {query}
        
        Return a JSON object with:
        - "type": "CHAT" or "RESEARCH"
        - "response": string (if CHAT, provide a friendly response here, else null)
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

        # Step 2: Collect (Research Mode)
        print("Starting Collection Phase...")
        collected_data = self.collector.collect(query, history)
        
        # Determine requested formats
        requested_formats = ["pdf"] # Default
        query_lower = query.lower()
        if "word" in query_lower or "docx" in query_lower:
            requested_formats.append("docx")
        if "excel" in query_lower or "spreadsheet" in query_lower or "csv" in query_lower:
            requested_formats.append("excel")

        # Step 3: Analyze
        print(f"Starting Analysis Phase (Formats: {requested_formats})...")
        analysis_result = self.analyzer.analyze(query, collected_data, history, requested_formats=requested_formats)
        
        report_content = analysis_result["report_content"]
        pdf_path = analysis_result["pdf_path"]
        sources = analysis_result["sources"]
        documents = analysis_result["documents"]

        # Step 3: Speak (Summary)
        # We'll ask the LLM to generate a brief spoken summary of the report
        summary_prompt = f"""
        Based on the following report, generate a concise, conversational summary suitable for speech (1-2 sentences).
        
        Report:
        {report_content}
        """
        # We can use the collector's LLM for this simple task
        summary = self.collector.llm.generate(summary_prompt, history=history, system_prompt="You are a helpful assistant. Be concise.")
        
        audio_bytes = self.tts_tool.speak(summary)

        return {
            "answer": report_content,
            "audio": audio_bytes,
            "sources": sources,
            "documents": documents,
            "pdf_path": pdf_path,
            "docx_path": analysis_result.get("docx_path"),
            "excel_path": analysis_result.get("excel_path")
        }
