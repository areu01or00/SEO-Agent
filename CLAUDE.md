# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
# Activate virtual environment (if exists)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install DataForSEO MCP server globally
npm install -g dataforseo-mcp-server

# Run the main application
streamlit run app.py
```

### Development Commands
```bash
# Test keyword research functionality
python -c "from agents.keyword_agent import KeywordAgent; agent = KeywordAgent(); print(agent._generate_mock_keywords('seo tools', 100, 70))"

# Test MCP connection directly
python -c "from mcp.client import DataForSEOMCP; client = DataForSEOMCP(); print(client.get_keyword_suggestions('seo', limit=5))"

# Format code (if black is installed)
black app.py agents/ utils/ mcp/

# Lint code (if flake8 is installed)
flake8 app.py agents/ utils/ mcp/
```

### Public Demo Commands
```bash
# Run public demo with LocalTunnel (may have firewall issues)
./start_public_demo.sh

# Alternative: Run public demo with ngrok (more reliable)
./start_public_demo_ngrok.sh
```

## Architecture Overview

This is a **Streamlit-based SEO keyword research tool** that integrates DataForSEO API through **Model Context Protocol (MCP)** with AI-powered analysis via OpenRouter LLMs.

### Core Architecture Pattern

```
Streamlit UI (app.py)
    ↓
KeywordAgent (agents/keyword_agent.py) 
    ↓
DataForSEOMCP (mcp/client.py) ← MCP Server Communication
    ↓
Enhanced Processing (mcp/enhanced_processing.py) ← Data transformation
    ↓
Results Display + AI Insights (LLMClient via OpenRouter)
```

### Key Design Decisions

1. **MCP Integration**: Uses subprocess communication with official `dataforseo-mcp-server` npm package, NOT direct API calls
2. **Fallback System**: All MCP calls have mock data fallbacks for development/testing
3. **Multi-tab Interface**: 6 distinct analysis tabs (Keywords, SERP, Competitors, Trends, Content, Reports)
4. **AI Enhancement**: LLM-powered insights for keyword clustering and content optimization

## Critical Components

### 1. MCP Communication (`mcp/client.py`)
- **MCPClient**: Generic MCP server communication via stdio
- **DataForSEOMCP**: Specific DataForSEO MCP integration with full API module support
- **Key Methods**: Uses official DataForSEO MCP tools like `dataforseo_labs_google_keyword_ideas`, `serp_organic_live_advanced`
- **Error Handling**: Graceful fallback to mock data when MCP fails

### 2. Data Processing (`mcp/enhanced_processing.py`)
- **Response Parsing**: Transforms raw DataForSEO JSON into Streamlit-friendly formats
- **Critical Functions**: 
  - `process_competitor_data()`: Skips first item (target domain), processes actual competitors
  - `process_trends_data()`: Handles `values[]` arrays and `date_from` fields from Google Trends
  - `process_content_analysis_data()`: Processes on-page SEO metrics with error detection
- **Mock Generators**: Fallback data generators for each analysis type

### 3. AI Integration (`utils/llm_client.py`)
- **OpenRouter Integration**: Uses OpenRouter API for multi-model LLM access
- **Model Configuration**: Configurable via `OPENROUTER_MODEL` environment variable
- **Token Management**: Optimized prompts with specific token limits (1500 for content insights)

### 4. Main Agent (`agents/keyword_agent.py`)
- **Unified Interface**: Single agent class for all SEO analysis functions
- **Method Pattern**: Each analysis type has dedicated method (e.g., `research_keywords()`, `analyze_serp()`, `analyze_competitor_domains()`)
- **Country/Language Mapping**: Converts codes to full names required by DataForSEO MCP

## Environment Configuration

**Required Environment Variables:**
```bash
# DataForSEO MCP Authentication
DATAFORSEO_USERNAME=your_username
DATAFORSEO_PASSWORD=your_password

# OpenRouter LLM Access  
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemini-2.0-flash-001  # or preferred model
```

## Troubleshooting Patterns

### MCP Connection Issues
- **Symptom**: "Expecting value: line 1 column 1 (char 0)" errors
- **Common Causes**: Missing environment variables, incorrect URL formats, DataForSEO API errors
- **Resolution**: Check processing functions handle empty responses and API error codes

### URL Handling
- **Content Analysis**: Requires full URLs with protocol (`https://domain.com` not `domain.com`)
- **Competitor Analysis**: Accepts URLs but extracts clean domain names via `extract_domain_from_input()`

### Data Processing Edge Cases
- **Trends Data**: Uses `values[0]` from arrays, skips `missing_data: true` entries
- **Competitor Data**: First item in results is target domain (should be skipped)
- **Content Analysis**: Check for `status_code != 20000` and handle API error messages

## Testing Notes

The application is designed to work with or without active MCP connections:
- **With MCP**: Real DataForSEO data via official MCP server
- **Without MCP**: Mock data generators provide realistic fallback data
- **Hybrid Mode**: Real data for some endpoints, mock for others based on availability

All data processing functions include comprehensive error handling and will gracefully fall back to mock data if MCP responses are malformed or empty.

## Tab-Specific Functionality

### Tab 1: Keyword Research (`research_keywords`)
- **MCP Tool**: `dataforseo_labs_google_keyword_ideas`
- **Filters**: Min volume, max difficulty
- **AI Enhancement**: Keyword clustering and content opportunities

### Tab 2: SERP Analysis (`analyze_serp`)
- **MCP Tool**: `serp_organic_live_advanced`
- **Data**: Top 10 ranking pages
- **AI Enhancement**: Content gap analysis

### Tab 3: Competitor Analysis (`analyze_competitor_domains`, `analyze_competitor_keywords`)
- **MCP Tools**: `dataforseo_labs_google_competitors_domain`, `dataforseo_labs_google_ranked_keywords`
- **Features**: Domain discovery + keyword intelligence

### Tab 4: Trends & Volume (`get_search_volume`, `get_trends`)
- **MCP Tools**: `keywords_data_google_ads_search_volume`, `keywords_data_google_trends_explore`
- **Time Ranges**: Past hour to 5 years

### Tab 5: Content Analysis (`analyze_content`)
- **MCP Tool**: `on_page_instant_pages`
- **Metrics**: OnPage score, technical SEO, readability
- **AI Enhancement**: 1500-token optimization recommendations

### Tab 6: Reports & Analytics
- **Export**: JSON and Excel with timestamps
- **Aggregation**: Cross-tab session data

### Tab 7: Content Brief (`generate_content_brief`)
- **AI Tool**: OpenRouter LLM for brief generation
- **Input**: Keywords from Tab 1 or manual entry, target audience, content type
- **Output**: Title suggestions, key topics, structure, word count, unique angles, CTAs
- **Export**: Text and JSON formats