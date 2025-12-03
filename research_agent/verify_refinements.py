import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research_agent.agent.research_agent import ResearchAgent

# Load env vars
load_dotenv(override=True)

def test_refinements():
    print("Initializing Research Agent...")
    agent = ResearchAgent()
    
    # Test 1: Chat Query
    print("\n--- Test 1: Chat Query ---")
    chat_query = "Hello, who are you?"
    chat_result = agent.process_query(chat_query)
    print(f"Query: {chat_query}")
    print(f"Answer: {chat_result['answer']}")
    if not chat_result['sources']:
        print("✅ Correctly identified as CHAT (no sources).")
    else:
        print("❌ Failed: Performed search for chat query.")

    # Test 2: Research Query (Default - PDF Only)
    print("\n--- Test 2: Research Query (Default) ---")
    research_query = "Latest advancements in nuclear fusion energy 2024"
    print(f"Query: {research_query}")
    research_result = agent.process_query(research_query)
    
    if research_result.get('pdf_path') and not research_result.get('docx_path'):
        print("✅ Correctly generated ONLY PDF (default).")
    else:
        print("❌ Failed: Generated extra files or missing PDF.")

    # Test 3: Research Query (With DOCX Request)
    print("\n--- Test 3: Research Query (With DOCX) ---")
    docx_query = "Research quantum computing and give me a word doc"
    print(f"Query: {docx_query}")
    docx_result = agent.process_query(docx_query)
    
    if docx_result.get('pdf_path') and docx_result.get('docx_path'):
        print("✅ Correctly generated PDF and DOCX.")
    else:
        print("❌ Failed: Missing PDF or DOCX.")

    # Check Documents (Aggressive Search)
    if docx_result['documents']:
        print(f"✅ Found {len(docx_result['documents'])} relevant documents.")
        for doc in docx_result['documents']:
            print(f"  - {doc['title']} ({doc['type']})")
    else:
        print("⚠️ No documents found.")

if __name__ == "__main__":
    test_refinements()
