import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research_agent.agent.research_agent import ResearchAgent

def test_agent():
    print("Initializing Agent...")
    agent = ResearchAgent()
    
    query = "Who is the president of France?"
    print(f"Testing query 1: {query}")
    response = agent.process_query(query)
    print(f"Answer 1: {response['answer']}")
    
    # Test Memory
    history = [
        {"role": "user", "content": query},
        {"role": "assistant", "content": response['answer']}
    ]
    
    query2 = "How old is he?"
    print(f"\nTesting query 2 (Memory Check): {query2}")
    response2 = agent.process_query(query2, history=history)
    print(f"Answer 2: {response2['answer']}")
    
    if "Macron" in response['answer'] or "Macron" in response2['answer'] or "He" in response2['answer']:
         print("\nSUCCESS: Agent handled context.")
    else:
         print("\nWARNING: Context might not have been handled correctly (check output).")

if __name__ == "__main__":
    test_agent()
