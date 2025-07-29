# BMM SEO Agent - Product Requirements Document

## 1. Overview

**Product Name**: BMM SEO Agent  
**Type**: Streamlit-based SEO keyword research tool with MCP integration  
**Core Purpose**: Automate keyword research using DataForSEO MCP tools and LLM analysis

## 2. Core Requirements

### User Interface
- **Framework**: Streamlit (simple, Python-based web UI)
- **Design**: Clean, functional interface similar to keyword-research-tool.html mockup

### Technology Stack
```
Frontend: Streamlit
Backend: Python
LLM Access: OpenRouter via LiteLLM  
MCP Integration: DataForSEO MCP Server
Agent Framework: LangChain (lightweight implementation)
```

## 3. Key Features

### 3.1 Keyword Research
- Input seed keywords
- Get keyword suggestions via DataForSEO MCP
- Display results in sortable table:
  - Keyword
  - Search Volume
  - Difficulty
  - CPC
  - Type (Related, Long-tail, Question)

### 3.2 Filters
- Country selection
- Language selection
- Minimum search volume
- Maximum difficulty

### 3.3 SERP Analysis
- Analyze top 10 results for selected keywords
- Show competitor URLs and titles
- Content gap analysis

### 3.4 Export
- CSV export
- Excel export

## 4. Technical Architecture

### Simple Architecture
```
Streamlit App
     │
     ├── LangChain Agent
     │        │
     │        ├── DataForSEO MCP Tools
     │        └── LiteLLM (OpenRouter)
     │
     └── Data Processing & Display
```

### Core Components

#### 1. Streamlit UI (`app.py`)
```python
import streamlit as st
from agents import KeywordAgent

st.title("BMM SEO Agent")

# Input section
seed_keyword = st.text_input("Enter seed keyword")
country = st.selectbox("Country", ["us", "uk", "ca", "au"])
language = st.selectbox("Language", ["en", "es", "fr", "de"])

if st.button("Generate Keywords"):
    agent = KeywordAgent()
    results = agent.research(seed_keyword, country, language)
    st.dataframe(results)
```

#### 2. LangChain Agent (`agents.py`)
```python
from langchain.agents import create_react_agent
from langchain.tools import Tool
import litellm

class KeywordAgent:
    def __init__(self):
        self.tools = [
            Tool(
                name="dataforseo_keywords",
                func=self.get_keywords,
                description="Get keyword suggestions"
            )
        ]
    
    def research(self, seed_keyword, country, language):
        # Agent logic with MCP tools
        pass
```

#### 3. MCP Configuration (`mcp_config.py`)
```python
MCP_CONFIG = {
    "dataforseo": {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-dataforseo"],
        "env": {
            "DATAFORSEO_LOGIN": os.getenv("DATAFORSEO_LOGIN"),
            "DATAFORSEO_PASSWORD": os.getenv("DATAFORSEO_PASSWORD")
        }
    }
}
```

## 5. Implementation Plan

### Phase 1: Basic Setup (Week 1)
- Set up Streamlit app structure
- Configure DataForSEO MCP
- Implement basic keyword research
- Simple table display

### Phase 2: Core Features (Week 2)
- Add filtering options
- Implement SERP analysis
- Add export functionality
- Basic error handling

### Phase 3: LLM Integration (Week 3)
- Integrate LiteLLM with OpenRouter
- Add keyword clustering
- Implement content suggestions
- Enhance insights

### Phase 4: Polish (Week 4)
- UI improvements
- Performance optimization
- Testing and bug fixes
- Documentation

## 6. UI Mockup (Streamlit)

```
┌─────────────────────────────────────┐
│      BMM SEO Agent                  │
├─────────────────────────────────────┤
│ Seed Keyword: [_______________]     │
│                                     │
│ Country: [US ▼]  Language: [EN ▼]  │
│                                     │
│ Min Volume: [___]  Max Diff: [___] │
│                                     │
│        [Generate Keywords]          │
├─────────────────────────────────────┤
│ Results:                            │
│ ┌─────────────────────────────────┐ │
│ │ Keyword | Volume | Diff | CPC   │ │
│ │ seo tool| 10,000 | 45   | $2.50 │ │
│ │ ...     | ...    | ...  | ...   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Export CSV] [Export Excel]         │
└─────────────────────────────────────┘
```

## 7. Key Files Structure

```
bmm-seo-agent/
├── app.py              # Main Streamlit app
├── agents/
│   ├── __init__.py
│   ├── keyword_agent.py
│   └── serp_agent.py
├── mcp/
│   ├── __init__.py
│   └── dataforseo.py
├── utils/
│   ├── __init__.py
│   ├── export.py
│   └── llm_client.py
├── requirements.txt
├── .env.example
└── README.md
```

## 8. Environment Variables

```bash
# .env file
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password
OPENROUTER_API_KEY=your_api_key
```

## 9. Dependencies

```txt
streamlit==1.28.0
langchain==0.1.0
litellm==1.0.0
pandas==2.0.0
python-dotenv==1.0.0
openpyxl==3.1.0  # for Excel export
```

## 10. MVP Deliverables

1. **Working Streamlit App** with:
   - Keyword input and generation
   - Results display in table format
   - Basic filtering options
   - CSV export

2. **MCP Integration**:
   - DataForSEO connection
   - Keyword suggestions API
   - SERP data retrieval

3. **Basic LLM Features**:
   - Keyword clustering
   - Simple insights generation

## 11. Future Enhancements (Post-MVP)

- DSPy integration for prompt optimization
- Additional MCP tools
- Advanced visualizations
- Batch processing
- API endpoints for programmatic access
- User authentication and projects

## 12. Success Criteria

- Generate 50+ keyword suggestions in < 5 seconds
- Accurate search volume and difficulty data
- Clean, responsive UI
- Stable MCP connection
- Meaningful LLM-generated insights