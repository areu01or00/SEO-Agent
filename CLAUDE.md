# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
# Activate virtual environment (if exists)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the main application
streamlit run app.py
```

### Development Commands
```bash
# Test REST API client directly
python -c "from utils.dataforseo_client import DataForSEOClient; client = DataForSEOClient(); print('Status:', 'Connected' if not client.use_fallback else 'Mock Mode')"

# Test keyword research functionality
python -c "from agents.keyword_agent import KeywordAgent; agent = KeywordAgent(); keywords = agent.research_keywords('seo tools', limit=5); print(f'Got {len(keywords)} keywords')"

# Test content generation
python -c "from agents.content_generator import ContentGeneratorAgent; agent = ContentGeneratorAgent(); result = agent.generate_content({'keyword': 'seo'}, 'Blog Post', 'marketers', 'Test Title', 500, use_mcp_research=False); print(f'Generated {len(result[\"content\"])} characters')"

# Format code (if black is installed)
black app.py agents/ utils/

# Lint code (if flake8 is installed)
flake8 app.py agents/ utils/
```

### Public Demo Commands
```bash
# Run public demo with LocalTunnel (may have firewall issues)
./start_public_demo.sh

# Alternative: Run public demo with ngrok (more reliable)
./start_public_demo_ngrok.sh
```

## Critical Architecture Changes

### **MAJOR PIVOT: MCP → REST API Integration**

**Historical Context:**
- **master_untouched branch**: Contains original MCP-based implementation
- **master branch**: Current REST API-based implementation (August 2025 pivot)

**Reason for Pivot:**
- **Streamlit Cloud Incompatibility**: MCP required Node.js ≥20, but Streamlit Cloud only had Node.js v12.22.12
- **Production Deployment Issues**: MCP server installation failed due to version conflicts and permission issues
- **Client Requirement**: Needed real DataForSEO data in production, not mock data

**Architecture Evolution:**
```
OLD (MCP-based):
Python App → subprocess → MCP Server (Node.js) → DataForSEO API

NEW (REST-based):
Python App → Direct HTTP calls → DataForSEO REST API
```

## Current Architecture Overview

This is a **Streamlit-based SEO keyword research tool** that integrates **directly with DataForSEO REST API** and AI-powered analysis via OpenRouter LLMs.

### Core Architecture Pattern

```
Streamlit UI (app.py) → 8 Analysis Tabs
    ↓
KeywordAgent (agents/keyword_agent.py) 
    ↓
DataForSEOClient (utils/dataforseo_client.py) ← Direct REST API calls
    ↓
Enhanced Processing ← Real-time data transformation
    ↓
Results Display + AI Insights (LLMClient via OpenRouter)
    ↓
ContentGeneratorAgent (agents/content_generator.py) ← Advanced content generation
```

### Key Design Decisions

1. **Direct REST API Integration**: Uses standard HTTP requests instead of MCP subprocess communication
2. **No Mock Data Fallbacks**: All API calls either return real data or fail transparently (removed per client request)
3. **Multi-tab Interface**: 8 distinct analysis tabs with real DataForSEO data
4. **AI Enhancement**: LLM-powered insights for keyword clustering, content optimization, and full content generation
5. **Keyword Preprocessing**: Automatic simplification of long/complex queries (>4 words) for better API results
6. **Streamlit Cloud Optimized**: Works perfectly on Streamlit Cloud without Node.js dependencies

## Critical Components

### 1. REST API Client (`utils/dataforseo_client.py`)
- **DataForSEOClient**: Direct HTTP integration with DataForSEO v3 API
- **Authentication**: Basic Auth using username/password (not API key)
- **Key Methods**: 
  - `get_keyword_suggestions()`: DataForSEO Labs keyword ideas
  - `get_serp_analysis()`: Live SERP organic results
  - `get_search_volume_data()`: Google Ads search volume data
  - `get_competitor_domains()`: Competitor domain analysis
  - `get_ranked_keywords()`: Domain ranking keywords
  - `get_trends_data()`: Google Trends exploration
  - `analyze_content()`: On-page content analysis
- **Error Handling**: Transparent failures (no mock fallbacks)
- **Keyword Preprocessing**: `_preprocess_keywords()` and `_simplify_keywords()` handle long queries

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
# DataForSEO REST API Authentication (username/password, NOT API key)
DATAFORSEO_USERNAME=your_username
DATAFORSEO_PASSWORD=your_password

# OpenRouter LLM Access  
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemini-2.5-flash-lite  # Current default model
```

**Streamlit Cloud Specific:**
```bash
STREAMLIT_RUNTIME_ENV=cloud  # Optional environment detection
```

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
- **No Node.js Required**: Pure Python implementation works on Streamlit Cloud
- **No Mock Data**: Failures are transparent (client requested removal of fallbacks)
- **Real Data Only**: All endpoints return actual DataForSEO data or empty results

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

## Recent Critical Fixes (August 2025)

1. **Content Analysis Zeros**: Fixed API response parsing for real data display
2. **Monthly Searches [object Object]**: Implemented proper array-to-string formatting
3. **API Status Display**: Updated to check correct authentication variables
4. **Competitor Analysis**: Mapped API response fields correctly
5. **Mock Data Removal**: Eliminated all fallback data per client requirements