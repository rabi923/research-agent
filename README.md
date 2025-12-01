# Multi-Model Research Agent

An intelligent research AI agent with multi-model architecture for deep research and analysis.

## Features

- 🔍 **Information Collector Agent**: Deeply searches the web using multiple queries and finds relevant documents (PDF, DOCX, XLSX)
- 📊 **Analyzer Agent**: Synthesizes collected data into detailed reports with PDF generation
- 🔊 **Text-to-Speech**: Provides audio summaries of research findings
- 🤖 **Multi-LLM Support**: Easily switch between OpenAI, Anthropic, and Google models

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/rabi923/research-agent.git
cd research-agent
```

2. Install dependencies:
```bash
pip install -r research_agent/requirements.txt
```

3. Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
```

4. Run the app:
```bash
streamlit run research_agent/ui/app.py
```

## Configuration

Edit `research_agent/config/settings.py` to configure:
- LLM temperature and model
- Default providers (LLM, Search, TTS)
- Report output directory

## License

MIT

