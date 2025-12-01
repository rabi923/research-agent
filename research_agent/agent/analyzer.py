import os
from fpdf import FPDF
from typing import List, Dict
from research_agent.core.llm.base import BaseLLMProvider
from research_agent.core.llm.factory import get_llm_provider
from research_agent.config.settings import settings

class AnalyzerAgent:
    def __init__(self):
        self.llm: BaseLLMProvider = get_llm_provider()
        self.output_dir = settings.REPORT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def analyze(self, query: str, collected_data: Dict, history: List[Dict] = []) -> Dict:
        """
        Analyze collected data and generate a report.
        """
        print(f"Analyzer Agent: Analyzing collected data for '{query}'...")
        
        context = collected_data.get("context", "")
        sources = collected_data.get("sources", [])
        documents = collected_data.get("documents", [])

        # Step 1: Generate Report Content (Markdown)
        report_prompt = f"""
        You are an expert Analyst. Your goal is to synthesize the collected information into a detailed, real-time report.
        
        User Query: {query}
        
        Collected Information:
        {context}
        
        Please generate a comprehensive report in Markdown format.
        Structure the report with:
        - Executive Summary
        - Detailed Analysis (broken down by key topics)
        - Key Findings
        - Conclusion
        - Relevant Documents (List the documents found: {documents})
        
        Do not hallucinate. Base your report strictly on the collected information.
        """
        
        report_content = self.llm.generate(report_prompt, history=history, system_prompt="You are a helpful analyst. Write detailed reports.")
        
        # Step 2: Generate PDF
        pdf_path = self._generate_pdf(query, report_content)
        
        return {
            "report_content": report_content,
            "pdf_path": pdf_path,
            "sources": sources,
            "documents": documents
        }

    def _generate_pdf(self, title: str, content: str) -> str:
        """
        Convert Markdown content to PDF.
        """
        pdf = FPDF()
        pdf.add_page()
        
        # Add a Unicode font (using standard fonts for now, might need custom font for full unicode support)
        # FPDF standard fonts don't support all unicode characters. 
        # For simplicity in this demo, we'll use standard font and replace unsupported chars if needed.
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Research Report: {title}", 0, 1, 'C')
        pdf.ln(10)
        
        # Content
        pdf.set_font("Arial", size=11)
        
        # Simple markdown parsing (very basic)
        for line in content.split('\n'):
            # Encode to latin-1 to avoid unicode errors with standard FPDF fonts
            # Ideally we should use a font that supports utf-8
            safe_line = line.encode('latin-1', 'replace').decode('latin-1')
            
            if line.startswith('# '):
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, safe_line.replace('# ', ''), 0, 1)
                pdf.set_font("Arial", size=11)
            elif line.startswith('## '):
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, safe_line.replace('## ', ''), 0, 1)
                pdf.set_font("Arial", size=11)
            else:
                pdf.multi_cell(0, 6, safe_line)
                
        filename = f"{title.replace(' ', '_').lower()}_report.pdf"
        # Sanitize filename
        filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c=='_' or c=='.']).rstrip()
        
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        print(f"Report saved to {filepath}")
        return filepath
