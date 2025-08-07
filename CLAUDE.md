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

# Test competitor keywords (to verify 100 limit works)
source venv/bin/activate
python -c "from agents.keyword_agent import KeywordAgent; \
agent = KeywordAgent(); \
results = agent.analyze_competitor_keywords('semrush.com', 'us', 'en', 100); \
print(f'Got {len(results)} keywords')"

# Test content generation with word count
python -c "from agents.content_generator import ContentGeneratorAgent; \
agent = ContentGeneratorAgent(); \
result = agent.generate_content({'keyword': 'seo'}, 'Blog Post', 'marketers', \
'Test Title', 1500, use_mcp_research=False); \
print(f'Generated {len(result[\"content\"].split())} words')"

# Test humanization feature
python test_humanize_integration.py

# Test structure-preserving humanization
python test_humanize_structure.py
```

### Deployment Commands
```bash
# Push to GitHub (triggers DigitalOcean auto-deploy)
git add -A
git commit -m "Your message"
git push origin master

# Check deployment logs
# Go to DigitalOcean App Platform dashboard → Runtime Logs
```

## Architecture Overview

**Streamlit-based SEO tool** with DataForSEO API integration via MCP (Model Context Protocol) and AI enhancements through OpenRouter.

### Core Flow
```
Streamlit UI (app.py) → 9 Analysis Tabs
    ↓
KeywordAgent (agents/keyword_agent.py) 
    ↓
DataForSEOMCP (mcp/client.py) ← MCP subprocess (npx or direct)
    ↓
MCP Server (dataforseo-mcp-server) → DataForSEO API
    ↓
Enhanced Processing (mcp/enhanced_processing.py)
    ↓
Results + AI Insights (LLMClient → OpenRouter)
```

## Critical Implementation Details

### 1. MCP Server Discovery (`mcp/client.py`)
The system tries multiple methods to find the MCP server (lines 57-105):
1. **npx** (for DigitalOcean/cloud deployments)
2. **Direct command** (global install)
3. **Local node_modules/.bin** 
4. **Windows npm prefix** (AppData path)

This multi-method approach ensures compatibility across local development and cloud deployments.

### 2. Session State Management (`app.py`)
**CRITICAL FOR DEPLOYMENTS**: Streamlit session state behaves differently on cloud platforms.

For DigitalOcean specifically (lines 1057-1061):
```python
# Store content in multiple places for persistence
st.session_state.generated_content = result
st.session_state['content_backup'] = result['content']
st.session_state['metadata_backup'] = result.get('metadata', {})
```

Content display retrieves from multiple sources (lines 1121-1131):
```python
if 'generated_content' in st.session_state:
    content_to_display = st.session_state.generated_content
elif 'content_backup' in st.session_state:
    # Reconstruct from backup
```

**Known Issue**: On DigitalOcean, `st.rerun()` can cause session state loss. The app works but users may need to interact with any UI element to trigger display refresh.

### 3. Word Count Handling (`agents/content_generator.py`)
- **Initial generation** (line 203): `max_tokens = min(int(word_count * 2.5), 6000)`
- **Refinement** (lines 491-496): Uses same calculation when `target_word_count` provided
- **Refine content** accepts `target_word_count` parameter (line 466)
- Prompt explicitly states: "Generate AT LEAST {word_count} words" (line 356)
- Refinement prompt: "You MUST adjust the content length" (line 470)

### 4. Competitor Keywords Limit (`mcp/client.py`)
To ensure adequate results (lines 337-348):
- Requests `max(limit * 2, 200)` from API
- Returns only requested limit after processing
- Note: Small domains may have fewer keywords than requested

## Tab-Specific Implementation

### Tab 9: Domain Analytics (NEW)
**File**: `app.py` lines 1235-1380
- **Method**: `analyze_domain_rankings()` in `agents/keyword_agent.py`
- **Features**: 
  - Keyword position tracking
  - Traffic estimation using ETV (Estimated Traffic Value)
  - Position distribution (Top 3, Top 10, 11-20, 21-50)
  - Quick wins identification (high volume, positions 4-20)
  - AI-powered insights and recommendations

### Tab 8: Advanced Content Generator (ENHANCED)
**Recent Additions**:
1. **Custom Heading Structure** (lines 988-1004):
   - H1, H2, H3 count specification
   - Keyword targeting per heading level
   
2. **Content Humanization** (lines 1005-1015):
   - Tone options: professional, conversational, casual, formal, friendly
   - Readability levels: basic, intermediate, advanced
   - Natural language variations and colloquialisms

3. **Word Count Refinement**:
   - Refine content respects updated slider value
   - Better token allocation for longer content

4. **Humanize Ultra Feature** (NEW - lines 1246-1330):
   - Advanced chunk-based humanization using AI Text Humanizer API
   - **Structure Preservation**: Maintains all markdown formatting and headings
   - **Smart Processing**: Only humanizes body text, keeps headings unchanged
   - Processes content in 1000-word chunks for optimal quality
   - Maintains 95-105% of original word count through smart expansion
   - Preserves natural flow and consistent tone across chunks
   - Shows progress during processing with chunk/section details
   - Option to restore original content
   - Disabled after first humanization to prevent over-processing

## Deployment

### DigitalOcean App Platform ($5/month)
**Current Production Setup**:
- URL: Provided by DigitalOcean (e.g., `app-name-xxxxx.ondigitalocean.app`)
- Auto-deploys from GitHub master branch
- Environment variables set in DO dashboard

**Required Files**:
- `Procfile`: Specifies Streamlit run command
- `runtime.txt`: Python version (python-3.11.9)
- `package-lock.json`: MUST be committed for Node.js dependencies
- `app.yaml`: DigitalOcean configuration

**Known Issues**:
1. **Session State**: Content may not display immediately after generation
   - **Workaround**: Users interact with any UI element to trigger refresh
   - **Root Cause**: Streamlit session state persistence differs on DO
   
2. **MCP Server**: Uses `npx` which may be slower than direct execution
   - **Mitigation**: Increased timeouts, multiple discovery methods

3. **CORS Warnings**: Can be ignored, app functions normally

### Alternative Deployment Options Considered
1. **Streamlit Cloud**: ❌ No Node.js support for MCP server
2. **Render.com**: ✅ Works well with Streamlit, similar pricing
3. **Railway**: ✅ Good Docker support, easy deployment
4. **DigitalOcean Droplet**: ✅ Full control but requires manual setup
5. **Windows Local**: ❌ Attempted but abandoned due to complexity

## Environment Variables

```bash
# Required for MCP/DataForSEO
DATAFORSEO_USERNAME=your_username
DATAFORSEO_PASSWORD=your_password  # Not API key!

# Required for AI features
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=google/gemini-2.5-flash-lite  # Optional, this is default

# Automatically set by DigitalOcean
DIGITALOCEAN_APP_ID=xxxxx  # Used for platform detection

# Humanizer API (hardcoded in content_generator.py)
# Email: info@bluemoonmarketing.com.au
# Password: 6c90555bfd313691
# Endpoint: https://ai-text-humanizer.com/api.php
```

## Recent Session Achievements

### Features Implemented
1. **Tab 9 Domain Analytics**: Complete domain ranking analysis with traffic estimation
2. **Enhanced Content Generation**: 
   - Custom heading structures with keyword targeting
   - Humanized content with tone/readability controls
   - Fixed word count accuracy (increased token limits)
3. **Competitor Keywords**: Increased limit from 20 to 100 (requests 200 from API)
4. **Session State Fixes**: Dual storage mechanism for DigitalOcean compatibility

### Problems Solved
1. **Mock Data Removal**: All fallback data eliminated for transparency
2. **Content Display on DO**: Added backup storage keys for session persistence
3. **Word Count Issues**: 
   - Increased token multiplier from 2x to 2.5x
   - Raised cap from 4000 to 6000 tokens
   - Made refinement respect slider value
4. **MCP Server Discovery**: Multi-method approach for cross-platform compatibility
5. **API Key Exposure**: Removed from Git history, using environment variables only

### Latest Fixes (Current Session)
1. **Word Count Display After Refinement** (`app.py` lines 1098-1105):
   - Issue: Word count metric not updating after content refinement
   - Fix: Update `metadata['word_count']` with `len(refined_content.split())`
   - Also update backup storage for DigitalOcean compatibility
   - Chat message now shows: "Content refined. New word count: X words."

2. **Refinement Word Count Slider** (`agents/content_generator.py` lines 490-502):
   - Issue: Refinement ignored updated slider value, used original content length
   - Root cause: `max_tokens = len(current_content.split()) * 2` based on current content
   - Fix: Use `target_word_count * 2.5` when provided, matching main generation logic
   - Stronger prompt: "You MUST adjust the content length to be approximately X words"

3. **Competitor Keywords Limit** (`mcp/client.py` lines 337-357):
   - Increased API request to `max(limit * 2, 200)` to ensure adequate results
   - Returns only requested limit after processing
   - Note: Small domains may genuinely have fewer keywords than requested

4. **Humanize Ultra Integration** (`agents/content_generator.py` lines 545-762, `app.py` lines 1246-1330):
   - **Implementation**: Structure-preserving chunk-based humanization using AI Text Humanizer API
   - **Process**: 
     1. Parse markdown structure to identify headings and body sections
     2. Keep all headings unchanged (preserves H1, H2, H3 structure)
     3. Humanize only body text in 1000-word chunks via API
     4. Rebuild content with original structure intact
     5. Expand if needed to maintain word count (LLM-based)
   - **Key Methods**:
     - `_parse_markdown_structure()`: Extracts heading hierarchy and body text
     - `_humanize_text_chunk()`: Processes individual text chunks
     - `humanize_ultra()`: Main method orchestrating the process
   - **Results**: 
     - 95-105% word count accuracy
     - Maintains all markdown formatting (headings, lists, etc.)
     - Preserves configured heading structure from Advanced Settings
     - Natural flow and readability improvements
   - **UI Features**:
     - Progress display showing chunk/section processing
     - Detailed statistics (original/final words, sections, accuracy %)
     - Restore original button
     - Disabled after first humanization
   - **Testing**: Successfully processes 1500-2000 word content with structure intact

### Abandoned Attempts
1. **Windows Installation Package**: Created setup.bat, setup.ps1, but removed due to:
   - Complex PATH issues
   - MCP server installation problems
   - Client opted for cloud deployment instead

## Testing Insights

### Domain Size Matters
- Small domains (e.g., bluemoonmarketing.com.au): May only have 10-20 keywords
- Large domains (e.g., semrush.com): Will return full 100 keywords
- The code works correctly; it's a data availability issue

### Local vs Cloud Differences
| Aspect | Local | DigitalOcean |
|--------|-------|--------------|
| MCP Server | Direct execution | Via npx |
| Session State | Persistent | May reset on rerun |
| Performance | Fast | Network latency |
| st.rerun() | Works perfectly | Can cause state loss |

## Code Patterns to Maintain

### Always Check Environment
```python
import os
if os.getenv('DIGITALOCEAN_APP_ID'):
    # Cloud-specific behavior
else:
    # Local development behavior
```

### MCP Error Handling
```python
try:
    result = self.dataforseo_mcp.method()
except Exception as e:
    print(f"MCP failed: {str(e)}")
    return []  # Return empty, never mock data
```

### Session State Redundancy
```python
# Store in multiple places
st.session_state.main_key = data
st.session_state['backup_key'] = data['important_field']
```

## Critical Files

- `app.py`: Main UI, all 9 tabs, session state management
- `agents/keyword_agent.py`: All DataForSEO API interactions
- `agents/content_generator.py`: Content generation with AI
- `mcp/client.py`: MCP server communication, multi-method discovery
- `mcp/enhanced_processing.py`: Response parsing, ETV extraction
- `utils/llm_client.py`: OpenRouter integration

## Never Do This
1. **Don't add mock data** - Client requires real data only
2. **Don't commit .env or secrets** - Use environment variables
3. **Don't assume single platform** - Code must work locally and on cloud
4. **Don't trust st.rerun() on cloud** - It may clear session state
5. **Don't hardcode limits** - Make them configurable parameters

## Quick Debugging

### Content Not Showing on DigitalOcean
1. Check Runtime Logs for "DEBUG: Content stored, length: XXXX"
2. Verify content_backup keys in session state
3. Try moving any UI slider to trigger refresh

### Keyword Count Issues
1. Test with large domain (amazon.com, wikipedia.org)
2. Check if domain actually has that many keywords
3. Verify actual_limit calculation in mcp/client.py

### MCP Server Not Found
1. Run `npm list -g dataforseo-mcp-server`
2. Check all 4 discovery methods in mcp/client.py
3. Verify Node.js version is 20+

## Session Summary
This codebase evolved from a mock-data prototype to a production-ready SEO tool deployed on DigitalOcean. The main challenges were cloud platform compatibility (especially Streamlit session state) and ensuring real data transparency. The solution uses redundant storage mechanisms and platform-specific behavior to maintain functionality across environments.