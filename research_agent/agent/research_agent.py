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
        1. Collect: Gather information and documents.
        2. Analyze: Generate report and PDF.
        3. Speak: Convert summary to audio.
        """
        
        # Step 1: Collect
        print("Starting Collection Phase...")
        collected_data = self.collector.collect(query, history)
        
        # Step 2: Analyze
        print("Starting Analysis Phase...")
        analysis_result = self.analyzer.analyze(query, collected_data, history)
        
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
            "pdf_path": pdf_path
        }
