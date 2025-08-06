# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
# Activate virtual environment (if exists)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install

# Run the main application locally
streamlit run app.py

# Run with public URL via LocalTunnel
./start_public_demo.sh
```

### Development Commands
```bash
# Test MCP client directly (requires environment variables)
DATAFORSEO_USERNAME="your_username" DATAFORSEO_PASSWORD="your_password" python -c "from mcp.client import DataForSEOMCP; client = DataForSEOMCP(); result = client.get_content_analysis('https://example.com'); print('MCP Status: Connected -', list(result.keys()))"

# Test keyword research functionality
DATAFORSEO_USERNAME="your_username" DATAFORSEO_PASSWORD="your_password" OPENROUTER_API_KEY="your_key" python -c "from agents.keyword_agent import KeywordAgent; agent = KeywordAgent(); keywords = agent.research_keywords('seo tools', limit=5); print(f'Got {len(keywords)} keywords')"

# Test content generation with real MCP research
DATAFORSEO_USERNAME="your_username" DATAFORSEO_PASSWORD="your_password" OPENROUTER_API_KEY="your_key" python -c "from agents.content_generator import ContentGeneratorAgent; agent = ContentGeneratorAgent(); result = agent.generate_content({'keyword': 'seo'}, 'Blog Post', 'marketers', 'Test Title', 500, use_mcp_research=True); print(f'Generated {len(result[\"content\"])} characters')"

# Format code (if black is installed)
black app.py agents/ utils/ mcp/

# Lint code (if flake8 is installed)
flake8 app.py agents/ utils/ mcp/
```

### Public Demo Commands
```bash
# Run public demo with LocalTunnel and MCP integration
./start_public_demo.sh
# This will give you: https://bmm-seo-tools.loca.lt
```

## Architecture Overview

This is a **Streamlit-based SEO keyword research tool** that integrates DataForSEO API through **Model Context Protocol (MCP)** with AI-powered analysis via OpenRouter LLMs.

### **Current Implementation: MCP-Based Integration**

**Why MCP:**
- **Full Control**: Local hosting with Node.js 20+ support
- **Subprocess Communication**: Direct MCP server integration for reliable DataForSEO access
- **Public Access**: LocalTunnel provides public URL (https://bmm-seo-tools.loca.lt)
- **No Platform Limitations**: Self-hosted solution avoids cloud platform restrictions

### Core Architecture Pattern

```
Streamlit UI (app.py) → 8 Analysis Tabs
    ↓
KeywordAgent (agents/keyword_agent.py) 
    ↓
DataForSEOMCP (mcp/client.py) ← MCP subprocess communication
    ↓
MCP Server (Node.js) → DataForSEO API → Enhanced Processing
    ↓
Results Display + AI Insights (LLMClient via OpenRouter)
    ↓
ContentGeneratorAgent (agents/content_generator.py) ← MCP research integration
```

### Key Design Decisions

1. **MCP Integration**: Uses subprocess communication with official `dataforseo-mcp-server` npm package
2. **No Fallback System**: All mock data removed - failures are transparent, returns empty results or raises exceptions
3. **Multi-tab Interface**: 8 distinct analysis tabs with real DataForSEO data only
4. **AI Enhancement**: LLM-powered insights for keyword clustering, content optimization, and full content generation
5. **Keyword Preprocessing**: Automatic simplification of long/complex queries (>4 words) for better API results
6. **LocalTunnel Integration**: Public URL access via https://bmm-seo-tools.loca.lt

## Critical Components

### 1. MCP Communication (`mcp/client.py`)
- **MCPClient**: Generic MCP server communication via stdio
- **DataForSEOMCP**: Specific DataForSEO MCP integration with full API module support
- **Key Methods**: Uses official DataForSEO MCP tools like:
  - `dataforseo_labs_google_keyword_ideas`: Keyword suggestions
  - `serp_organic_live_advanced`: Live SERP analysis
  - `keywords_data_google_ads_search_volume`: Search volume data
  - `dataforseo_labs_google_competitors_domain`: Competitor analysis
  - `dataforseo_labs_google_ranked_keywords`: Domain ranking data
  - `keywords_data_google_trends_explore`: Google Trends data
  - `on_page_instant_pages`: Content analysis
- **Error Handling**: Raises exceptions when MCP fails - no mock data fallbacks
- **Keyword Preprocessing**: `_preprocess_keywords()` and `_simplify_keywords()` handle long queries (>4 words)

### 2. Agent Layer (`agents/keyword_agent.py`)
- **Unified Interface**: Single agent class for all SEO analysis functions
- **Method Pattern**: Each analysis type has dedicated method with location/language mapping
- **AI Integration**: Enhanced results with LLM-powered insights
- **Country/Language Mapping**: Converts codes to full names required by DataForSEO API

### 3. Advanced Content Generation (`agents/content_generator.py`)
- **ContentGeneratorAgent**: Sophisticated content creation with 5 content type templates
- **MCP Research Integration**: Uses real-time SERP and keyword data for content enhancement
- **Chat Interface Support**: Handles conversation history and content refinement
- **Improvement Suggestions**: AI-powered content analysis across 5 areas (SEO, readability, structure, CTA, audience)
- **Export Capabilities**: Markdown, Text, and HTML formats

### 4. AI Integration (`utils/llm_client.py`)
- **OpenRouter Integration**: Multi-model LLM access with configurable models
- **Model Configuration**: Defaults to `google/gemini-2.5-flash-lite` (August 2025)
- **Token Management**: Optimized prompts with specific limits (1500 for insights, 800 for suggestions)

### 5. Legacy MCP Components (`mcp/` directory)
- **Status**: Preserved for reference but NOT used in current implementation
- **Purpose**: Historical MCP-based integration (see master_untouched branch)
- **Note**: These files exist but are not imported or used by the current REST implementation

## Environment Configuration

**Required Environment Variables:**
```bash
# DataForSEO MCP Authentication
DATAFORSEO_USERNAME=your_username
DATAFORSEO_PASSWORD=your_password

# OpenRouter LLM Access  
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemini-2.5-flash-lite  # default model
```

## Public Demo with LocalTunnel

### **Quick Start:**
```bash
./start_public_demo.sh
```

**What it does:**
1. **Sets environment variables** for MCP authentication
2. **Installs dependencies** (npm packages including dataforseo-mcp-server)
3. **Starts Streamlit** with MCP integration
4. **Creates public URL** via LocalTunnel: https://bmm-seo-tools.loca.lt

### **Features:**
- ✅ **Public Access**: Share URL with anyone worldwide
- ✅ **Real DataForSEO Data**: Full MCP integration with live API
- ✅ **All 8 Tabs Working**: Complete functionality
- ✅ **AI-Powered Insights**: OpenRouter LLM integration
- ✅ **Custom Subdomain**: Professional URL (bmm-seo-tools.loca.lt)

### **Requirements:**
- **Node.js 20+**: Required for MCP server (check with `node --version`)
- **Python 3.x**: For Streamlit application
- **Internet Connection**: For LocalTunnel and DataForSEO API access

## Data Processing Architecture

### API Response Handling
- **Keyword Data**: Direct processing of DataForSEO Labs responses
- **SERP Data**: Real-time Google organic results parsing
- **Volume Data**: Monthly search data with formatted display (prevents [object Object] issues)
- **Competitor Data**: Domain intersection and ranking analysis
- **Content Analysis**: On-page SEO metrics with proper field mapping

### Critical Data Structure Updates
- **Monthly Searches**: Processes array of objects into readable strings (`"2025-06: 165,000, 2025-05: 135,000"`)
- **Content Metrics**: Nested structure handling (`content_metrics`, `meta`, `seo_checks`)
- **Competitor Data**: Proper field mapping for `relevant_serp_items`, `intersections`, `etv`

## Troubleshooting Patterns

### REST API Issues
- **Authentication**: Use username/password, not API key
- **URL Handling**: Content analysis requires full URLs with protocol
- **Long Keywords**: Automatically simplified (>4 words → first 4 words) for better results
- **Monthly Data**: Formatted as readable strings to avoid display issues

### Streamlit Widget Issues
- **Unique Keys**: All input widgets have unique keys (e.g., `keyword_research_input`)
- **Session State**: Content generation uses proper session state management
- **Data Display**: Handles nested API responses correctly

### Deployment Considerations
- **Node.js Required**: MCP server needs Node.js 20+ for dataforseo-mcp-server package
- **No Mock Data**: All fallbacks removed - failures raise exceptions or return empty results
- **Real Data Only**: All endpoints return actual DataForSEO data or fail transparently
- **Environment Variables**: Must be set correctly or initialization fails

## Tab-Specific Implementation

### Tab 1: Keyword Research
- **API**: `dataforseo_labs_google_keyword_ideas`
- **Features**: Volume filtering, difficulty scoring, AI clustering
- **Preprocessing**: Long keywords automatically simplified for better results

### Tab 2: SERP Analysis
- **API**: `serp_organic_live_advanced`
- **Features**: Top 10 results, AI gap analysis, competitive insights
- **Preprocessing**: Query simplification for complex searches

### Tab 3: Competitor Analysis
- **APIs**: `dataforseo_labs_google_competitors_domain`, `dataforseo_labs_google_ranked_keywords`
- **Features**: Domain discovery, keyword intelligence, intersection analysis
- **URL Handling**: Automatic domain extraction from full URLs

### Tab 4: Trends & Volume
- **APIs**: `keywords_data_google_ads_search_volume`, `keywords_data_google_trends_explore`
- **Features**: Historical data, search volume trends, seasonal patterns
- **Data Processing**: Monthly searches formatted for display, trends data with proper date handling

### Tab 5: Content Analysis
- **API**: `on_page_instant_pages`
- **Features**: OnPage scoring, technical SEO analysis, content metrics
- **Data Structure**: Handles nested response format (no `onpage_result` wrapper)
- **URL Processing**: Automatic HTTPS addition for bare domains

### Tab 6: Reports & Analytics
- **Features**: JSON and Excel export with timestamps
- **Data**: Aggregated cross-tab session data

### Tab 7: Content Brief Generation
- **AI Tool**: OpenRouter LLM integration
- **Features**: Keyword-based briefs, audience targeting, content structure
- **Export**: Text and JSON formats

### Tab 8: Advanced Content Generator
- **Features**: 5 content templates, real-time research integration, chat interface
- **Content Types**: Blog Post, Landing Page, Product Page, Guide/Tutorial, Comparison Article
- **Advanced**: Word count control (500-4000), refinement chat, improvement suggestions
- **Export**: Markdown, Text, HTML formats with proper rendering

## Important Implementation Notes

### API Authentication Changes
- **OLD**: Used `DATAFORSEO_API_KEY` environment variable
- **NEW**: Uses `DATAFORSEO_USERNAME` and `DATAFORSEO_PASSWORD` for Basic Auth
- **UI Status**: Fixed to check correct environment variables

### Content Analysis Evolution
- **Issue**: Original expected `onpage_result` wrapper that doesn't exist in API
- **Fix**: Data extracted directly from main response object
- **Result**: Real metrics (95.24/100 scores, actual word counts, page sizes)

### Mock Data Removal
- **Client Request**: Remove all mock/fallback data to ensure transparency
- **Implementation**: All methods return empty results if API fails
- **Benefit**: Clear visibility when API issues occur

### Keyword Processing Intelligence
- **Long Query Handling**: Queries >4 words automatically simplified
- **Example**: "top 10 cheese burger restaurants in sydney" → "top cheese burger restaurants"
- **Applied To**: Keyword suggestions, SERP analysis, search volume, trends data
- **Result**: Better API response rates for complex queries

## Git Branch Strategy

- **master**: Current production branch with REST API implementation
- **master_untouched**: Historical MCP-based implementation (preserved for reference)
- **Deployment**: Use master branch for all deployments (Streamlit Cloud compatible)

## Recent Critical Fixes (Latest Session)

### Mock Data Elimination
- **Issue**: Mock data was masking real API failures and displaying fake results
- **Fix**: Completely removed all mock data generators and fallback systems
- **Files Modified**: `mcp/client.py`, `mcp/enhanced_processing.py`, `agents/keyword_agent.py`
- **Result**: Failures now raise exceptions immediately, ensuring data transparency

### Content Analysis Field Mapping Fix
- **Issue**: Content analysis showing OnPage Score 93.4 but Word Count/Load Time/Page Size as 0
- **Root Cause**: Streamlit app was looking for data in wrong nested structure
- **Fix**: Updated field mappings in `app.py` to match actual MCP response structure:
  - `content_data.get('word_count')` instead of `content_data.get('content_metrics', {}).get('word_count')`
  - `content_data.get('load_time')` instead of `content_data.get('page_timing', {}).get('load_time')`
  - `content_data.get('page_size')` instead of `content_data.get('content_metrics', {}).get('page_size')`
- **Result**: Now displays real values (Word Count: 26, Load Time: 503ms, Page Size: 1248 bytes)

### MCP Client Error Handling Improvements  
- **Issue**: `'DataForSEOMCP' object has no attribute 'use_fallback'` error
- **Fix**: Removed all references to `use_fallback` attribute across codebase
- **Files Modified**: `mcp/client.py`, `agents/keyword_agent.py`
- **Result**: Clean initialization without attribute errors

### Environment Variable Validation
- **Issue**: MCP client failing with "expected str, bytes or os.PathLike object, not NoneType"
- **Fix**: Added proper validation for required environment variables in `mcp/client.py`
- **Result**: Clear error messages when credentials are missing instead of cryptic errors

### Content Generator MCP Integration Fix
- **Issue**: ContentGeneratorAgent still importing old REST client
- **Fix**: Updated to use MCP client (`from mcp.client import DataForSEOMCP`)
- **Result**: Content generation now uses real-time MCP research data