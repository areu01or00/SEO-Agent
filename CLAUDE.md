# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install -g dataforseo-mcp-server  # Global install recommended
npm install  # Local dependencies

# Run locally
streamlit run app.py

# Run with public URL via LocalTunnel
./start_public_demo.sh
# This will give you: https://bmm-seo-tools.loca.lt
```

### Testing Commands
```bash
# Test MCP client connectivity
DATAFORSEO_USERNAME="your_username" DATAFORSEO_PASSWORD="your_password" \
python -c "from mcp.client import DataForSEOMCP; client = DataForSEOMCP(); \
result = client.get_keyword_suggestions('test', limit=5); print(f'Got {len(result)} keywords')"

# Test Trafilatura content extraction (PRIMARY method)
python -c "from utils.content_extractor import ContentExtractor; \
extractor = ContentExtractor(); \
result = extractor.extract_content('https://example.com'); \
print(f'Extracted: {result.get(\"title\")}')"

# Test content generation with word count
python -c "from agents.content_generator import ContentGeneratorAgent; \
agent = ContentGeneratorAgent(); \
result = agent.generate_content({'keyword': 'seo'}, 'Blog Post', 'marketers', \
'Test Title', 1500, use_mcp_research=False); \
print(f'Generated {len(result[\"content\"].split())} words')"

# Test humanization feature
python test_humanize_integration.py
python test_humanize_structure.py
```

## Architecture Overview

**Streamlit-based SEO tool** with dual content extraction (Trafilatura primary, DataForSEO secondary), AI-powered content generation with humanization, and comprehensive SEO analysis.

### Core Flow
```
Streamlit UI (app.py) → 9 Analysis Tabs
    ↓
KeywordAgent (agents/keyword_agent.py) 
    ↓
Content Extraction (TWO methods):
  PRIMARY: Trafilatura (utils/content_extractor.py) → Works on ALL sites including Cloudflare-protected
  SECONDARY: DataForSEOMCP (mcp/client.py) → For additional metrics only
    ↓
Enhanced Processing & AI Insights (LLMClient → OpenRouter)
    ↓
Content Generation (agents/content_generator.py) with Humanize Ultra feature
```

## Critical Implementation Details

### 1. Content Extraction Strategy (`agents/keyword_agent.py:229-287`)
**Trafilatura is PRIMARY** - always tries first:
1. Extract with Trafilatura (works on Cloudflare-protected sites)
2. Optionally enhance with DataForSEO metrics (if not blocked)
3. Fall back to DataForSEO only if Trafilatura fails

This ensures 100% success rate for content analysis, even on protected sites.

### 2. Humanize Ultra Feature (`agents/content_generator.py:544-762`)
Advanced content humanization using AI Text Humanizer API:
- **Structure Preservation**: Parses markdown, keeps headings unchanged
- **Chunk Processing**: 1000-word chunks for optimal quality
- **Smart Expansion**: Maintains 95-105% word count accuracy
- **Methods**:
  - `_parse_markdown_structure()`: Extracts heading hierarchy
  - `_humanize_text_chunk()`: Processes individual chunks
  - `humanize_ultra()`: Main orchestration

### 3. Session State Management (`app.py`)
**CRITICAL FOR DEPLOYMENTS**: Dual storage for cloud compatibility
```python
# Store in multiple places for persistence
st.session_state.generated_content = result
st.session_state['content_backup'] = result['content']
st.session_state['metadata_backup'] = result.get('metadata', {})
```

### 4. MCP Server Discovery (`mcp/client.py:57-105`)
Multi-method approach for cross-platform compatibility:
1. **npx** (DigitalOcean/cloud deployments)
2. **Direct command** (global install)
3. **Local node_modules/.bin**
4. **Windows npm prefix**

## Tab-Specific Implementation

### Tab 5: Content Analysis (ENHANCED)
- **Primary**: Trafilatura extraction (always works)
- **Secondary**: DataForSEO for performance metrics
- **Cloudflare Bypass**: Automatic via Trafilatura
- **AI Insights**: Generated for all extracted content

### Tab 8: Advanced Content Generator
**Features**:
1. **Custom Heading Structure** (lines 988-1004)
2. **Humanize Ultra Button** (lines 1246-1330)
3. **Word Count Refinement** (respects slider updates)
4. **Structure Preservation** during humanization

### Tab 9: Domain Analytics
- Keyword position tracking
- Traffic estimation (ETV)
- Quick wins identification
- AI-powered recommendations

## Environment Variables

```bash
# Required for MCP/DataForSEO
DATAFORSEO_USERNAME=your_username
DATAFORSEO_PASSWORD=your_password  # Not API key!

# Required for AI features
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=google/gemini-2.5-flash-lite  # Optional

# Humanizer API (hardcoded in content_generator.py)
# Email: info@bluemoonmarketing.com.au
# Password: 6c90555bfd313691
# Endpoint: https://ai-text-humanizer.com/api.php
```

## Deployment (DigitalOcean)

### Required Files
- `Procfile`: Streamlit run command
- `runtime.txt`: Python version (python-3.11.9)
- `package-lock.json`: Node.js dependencies
- `requirements.txt`: Python packages including `trafilatura` and `bs4`

### Known Issues
1. **Session State**: May reset on `st.rerun()` - use backup keys
2. **MCP Server**: Uses `npx` (slower than direct)
3. **Protected Sites**: DataForSEO blocked, Trafilatura works

## Latest Session Updates

### Content Analysis Improvements
1. **Trafilatura Primary**: No longer fallback, now main method
2. **Cloudflare Bypass**: Automatic via Trafilatura
3. **Fixed Display Issues**: Title, meta description, headings now show correctly
4. **SEO Checks Fixed**: Proper detection of title, description, H1 presence

### Humanization Feature
1. **Chunk-based Processing**: 1000-word chunks
2. **Structure Preservation**: Maintains all markdown/headings
3. **Word Count Accuracy**: 95-105% of target
4. **UI Integration**: Button in Content Generator tab

### Bug Fixes
1. **Word Count Update**: Now updates after refinement (line 1101)
2. **Refinement Slider**: Respects updated values (line 1095)
3. **View Full Analysis**: Fixed to display AI insights properly

## Code Patterns

### Content Extraction Pattern
```python
# Always try Trafilatura first
extractor = ContentExtractor()
content_data = extractor.extract_content(url)

# Optionally enhance with DataForSEO
if enable_javascript:
    mcp_data = self.dataforseo_mcp.get_content_analysis(url)
    if not 'Robot Challenge' in mcp_data.get('title', ''):
        # Merge performance metrics
```

### Error Handling
```python
# Never use mock data - return empty or raise
try:
    result = self.dataforseo_mcp.method()
except Exception as e:
    print(f"MCP failed: {str(e)}")
    return []  # Return empty, never mock
```

### Session State Redundancy
```python
# Store in multiple places for cloud deployments
st.session_state.main_key = data
st.session_state['backup_key'] = data['important_field']
```

## Critical Files

- `app.py`: Main UI, 9 tabs, session management
- `agents/keyword_agent.py`: DataForSEO integration, content analysis orchestration
- `agents/content_generator.py`: Content generation, humanization
- `utils/content_extractor.py`: Trafilatura-based extraction (NEW)
- `mcp/client.py`: MCP server communication
- `utils/llm_client.py`: OpenRouter integration

## Testing Insights

### Content Analysis
- **Protected Sites**: Trafilatura succeeds where DataForSEO fails
- **Example**: bluemoonmarketing.com.au (Cloudflare) works with Trafilatura
- **Metrics**: OnPage score, word count, SEO checks all functional

### Humanization
- **Chunk Processing**: ~5% reduction per 1000-word chunk
- **Accuracy**: Achieves 95-105% of target word count
- **Quality**: Maintains readability and natural flow

## Never Do This
1. **Don't add mock data** - Client requires real data only
2. **Don't assume DataForSEO works** - Always have Trafilatura ready
3. **Don't trust st.rerun() on cloud** - Use backup session keys
4. **Don't modify heading structure** during humanization
5. **Don't commit API keys** - Use environment variables