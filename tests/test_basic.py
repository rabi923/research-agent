import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent.config.settings import settings
from research_agent.agent.research_agent import ResearchAgent

def test_settings_load():
    """Test that settings can be loaded."""
    assert settings is not None
    # We don't check for specific values as they depend on .env
    # but the object should exist.

def test_research_agent_init():
    """Test that ResearchAgent can be initialized."""
    agent = ResearchAgent(use_deep_research=False)
    assert agent is not None
    assert agent.collector is not None
    assert agent.analyzer is not None

def test_exa_search_mode_toggle():
    """Test that deep research flag can be toggled."""
    agent_standard = ResearchAgent(use_deep_research=False)
    assert agent_standard.use_deep_research is False
    
    agent_deep = ResearchAgent(use_deep_research=True)
    assert agent_deep.use_deep_research is True
