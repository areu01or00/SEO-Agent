import streamlit as st
import pandas as pd
from agents.keyword_agent import KeywordAgent
from utils.export import export_to_csv, export_to_excel
import os
import json
import math
import random
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def extract_domain_from_input(domain_input: str) -> str:
    """Extract clean domain from user input (handles URLs)"""
    if not domain_input:
        return ""
    
    # Remove whitespace
    domain_input = domain_input.strip()
    
    # If it looks like a URL, parse it
    if domain_input.startswith(('http://', 'https://', 'www.')):
        if domain_input.startswith('www.'):
            domain_input = 'https://' + domain_input
        
        parsed = urlparse(domain_input)
        domain = parsed.netloc
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    
    # If it's already a clean domain, return as is
    return domain_input

# Page configuration
st.set_page_config(
    page_title="BMM SEO Agent",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        background-color: #667eea;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #764ba2;
        transform: translateY(-2px);
    }
    .dataframe {
        font-size: 14px;
    }
    .difficulty-easy {
        background-color: #4caf50;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
    }
    .difficulty-medium {
        background-color: #ff9800;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
    }
    .difficulty-hard {
        background-color: #f44336;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🔍 BMM SEO Agent")
st.markdown("**Intelligent Keyword Research powered by AI and DataForSEO**")

# Initialize session state
if 'keywords_data' not in st.session_state:
    st.session_state.keywords_data = None
if 'serp_data' not in st.session_state:
    st.session_state.serp_data = None

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🔑 Keyword Research", 
    "📊 SERP Analysis", 
    "🏆 Competitor Analysis",
    "📈 Trends & Volume",
    "🔍 Content Analysis",
    "📋 Reports",
    "📝 Content Brief",
    "✍️ Content Generator",
    "🌐 Domain Analytics"
])

with tab1:
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        seed_keyword = st.text_input(
            "Enter your seed keyword",
            key="keyword_research_input",
            placeholder="e.g., SEO tools, digital marketing, etc."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("Generate Keywords", type="primary", use_container_width=True)
    
    # Filters
    st.markdown("### 🎯 Filters")
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        country = st.selectbox(
            "Country",
            options=["us", "uk", "ca", "au", "in", "de", "fr", "es", "br", "jp"],
            format_func=lambda x: {
                "us": "🇺🇸 United States",
                "uk": "🇬🇧 United Kingdom",
                "ca": "🇨🇦 Canada",
                "au": "🇦🇺 Australia",
                "in": "🇮🇳 India",
                "de": "🇩🇪 Germany",
                "fr": "🇫🇷 France",
                "es": "🇪🇸 Spain",
                "br": "🇧🇷 Brazil",
                "jp": "🇯🇵 Japan"
            }.get(x, x)
        )
    
    with filter_col2:
        language = st.selectbox(
            "Language",
            options=["en", "es", "fr", "de", "pt", "it", "ja", "ko", "zh", "hi"],
            format_func=lambda x: {
                "en": "English",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "pt": "Portuguese",
                "it": "Italian",
                "ja": "Japanese",
                "ko": "Korean",
                "zh": "Chinese",
                "hi": "Hindi"
            }.get(x, x)
        )
    
    with filter_col3:
        min_volume = st.number_input("Min Search Volume", min_value=0, value=100, step=100)
    
    with filter_col4:
        max_difficulty = st.number_input("Max Difficulty", min_value=0, max_value=100, value=70, step=10)
    
    # Generate keywords
    if generate_button and seed_keyword:
        with st.spinner("🔄 Generating keyword ideas..."):
            try:
                # Initialize agent
                agent = KeywordAgent()
                
                # Get keywords
                keywords_data = agent.research_keywords(
                    seed_keyword=seed_keyword,
                    country=country,
                    language=language,
                    min_volume=min_volume,
                    max_difficulty=max_difficulty
                )
                
                # Store in session state
                st.session_state.keywords_data = keywords_data
                
                # Success message
                st.success(f"✅ Generated {len(keywords_data)} keyword suggestions!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display results
    if st.session_state.keywords_data is not None:
        st.markdown("### 📊 Keyword Results")
        
        # Statistics
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        df = pd.DataFrame(st.session_state.keywords_data)
        
        with stats_col1:
            st.metric("Total Keywords", len(df))
        
        with stats_col2:
            avg_volume = df['search_volume'].mean() if not df.empty else 0
            st.metric("Avg. Volume", f"{avg_volume:,.0f}")
        
        with stats_col3:
            avg_difficulty = df['difficulty'].mean() if not df.empty else 0
            st.metric("Avg. Difficulty", f"{avg_difficulty:.0f}")
        
        with stats_col4:
            avg_cpc = df['cpc'].mean() if not df.empty else 0
            st.metric("Avg. CPC", f"${avg_cpc:.2f}")
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            column_config={
                "keyword": st.column_config.TextColumn("Keyword", width="medium"),
                "search_volume": st.column_config.NumberColumn("Search Volume", format="%d"),
                "difficulty": st.column_config.NumberColumn("Difficulty", format="%d"),
                "cpc": st.column_config.NumberColumn("CPC", format="$%.2f"),
                "type": st.column_config.TextColumn("Type", width="small"),
            }
        )
        
        # Export buttons
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            csv_data = export_to_csv(df)
            st.download_button(
                label="📥 Export as CSV",
                data=csv_data,
                file_name=f"keywords_{seed_keyword.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        
        with export_col2:
            excel_data = export_to_excel(df)
            st.download_button(
                label="📥 Export as Excel",
                data=excel_data,
                file_name=f"keywords_{seed_keyword.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with tab2:
    st.markdown("### 🔍 SERP Analysis")
    
    if st.session_state.keywords_data is not None:
        # Select keyword for SERP analysis
        keywords_list = [kw['keyword'] for kw in st.session_state.keywords_data]
        selected_keyword = st.selectbox("Select a keyword to analyze", keywords_list)
        
        if st.button("Analyze SERP", type="primary"):
            with st.spinner("🔄 Analyzing SERP results..."):
                try:
                    agent = KeywordAgent()
                    serp_data = agent.analyze_serp(selected_keyword, country, language)
                    st.session_state.serp_data = serp_data
                    st.success(f"✅ SERP analysis complete for '{selected_keyword}'")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Display SERP results
        if st.session_state.serp_data is not None:
            st.markdown("#### Top Ranking Pages")
            
            for idx, result in enumerate(st.session_state.serp_data[:10], 1):
                with st.expander(f"#{idx} - {result.get('title', 'No title')}", expanded=(idx <= 3)):
                    st.markdown(f"**URL:** {result.get('url', '')}")
                    st.markdown(f"**Description:** {result.get('description', '')}")
                    
                    # Additional insights
                    if 'insights' in result:
                        st.markdown("**AI Insights:**")
                        st.info(result['insights'])
    else:
        st.info("👆 Please generate keywords first in the Keyword Research tab")

with tab3:
    st.markdown("### 🏆 Competitor Analysis")
    
    competitor_col1, competitor_col2 = st.columns(2)
    
    with competitor_col1:
        st.markdown("#### 🔍 Analyze Competitor Domain")
        competitor_domain = st.text_input(
            "Enter competitor domain",
            key="competitor_domain_input",
            placeholder="e.g., semrush.com, ahrefs.com"
        )
        
        if st.button("Analyze Competitors", type="primary"):
            if competitor_domain:
                # Extract clean domain from input
                clean_domain = extract_domain_from_input(competitor_domain)
                st.info(f"🔍 Finding competitors for: {clean_domain}")
                
                with st.spinner("🔄 Finding competitors..."):
                    try:
                        agent = KeywordAgent()
                        competitors = agent.analyze_competitor_domains(clean_domain, country, language, 10)
                        
                        if competitors:
                            st.success(f"✅ Found {len(competitors)} competitors!")
                            
                            # Display competitors table
                            competitor_df = pd.DataFrame(competitors)
                            st.dataframe(
                                competitor_df,
                                use_container_width=True,
                                column_config={
                                    "domain": st.column_config.TextColumn("Domain"),
                                    "common_keywords": st.column_config.NumberColumn("Common Keywords"),
                                    "estimated_traffic": st.column_config.NumberColumn("Est. Traffic"),
                                    "avg_position": st.column_config.NumberColumn("Avg. Position", format="%.1f"),
                                    "relevance": st.column_config.NumberColumn("Relevance", format="%.2f")
                                }
                            )
                        else:
                            st.warning("No competitors found")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with competitor_col2:
        st.markdown("#### 📊 Competitor Keywords")
        if competitor_domain:
            if st.button("Get Competitor Keywords"):
                # Extract clean domain from input
                clean_domain = extract_domain_from_input(competitor_domain)
                st.info(f"📊 Analyzing keywords for: {clean_domain}")
                
                with st.spinner("🔄 Analyzing competitor keywords..."):
                    try:
                        agent = KeywordAgent()
                        competitor_keywords = agent.analyze_competitor_keywords(clean_domain, country, language, 100)  # Increased from 20 to 100
                        
                        if competitor_keywords:
                            st.success(f"✅ Found {len(competitor_keywords)} competitor keywords!")
                            
                            # Display competitor keywords
                            comp_kw_df = pd.DataFrame(competitor_keywords)
                            st.dataframe(
                                comp_kw_df,
                                use_container_width=True,
                                height=400
                            )
                        else:
                            st.warning("No competitor keywords found")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

with tab4:
    st.markdown("### 📈 Trends & Volume Analysis")
    
    trends_col1, trends_col2 = st.columns(2)
    
    with trends_col1:
        st.markdown("#### 📊 Search Volume Data")
        volume_keywords = st.text_area(
            "Enter keywords (one per line):",
            key="volume_keywords_input",
            placeholder="seo tools\ndigital marketing\nkeyword research"
        )
        
        if st.button("Get Volume Data", type="primary"):
            if volume_keywords:
                keywords_list = [kw.strip() for kw in volume_keywords.split('\n') if kw.strip()]
                
                with st.spinner("🔄 Getting search volume data..."):
                    try:
                        agent = KeywordAgent()
                        volume_data = agent.get_search_volume_trends(keywords_list, country, language)
                        
                        if volume_data:
                            st.success(f"✅ Retrieved volume data for {len(volume_data)} keywords!")
                            
                            # Display volume data
                            volume_df = pd.DataFrame(volume_data)
                            st.dataframe(
                                volume_df,
                                use_container_width=True,
                                column_config={
                                    "keyword": st.column_config.TextColumn("Keyword"),
                                    "search_volume": st.column_config.NumberColumn("Search Volume", format="%d"),
                                    "cpc": st.column_config.NumberColumn("CPC", format="$%.2f"),
                                    "competition_level": st.column_config.TextColumn("Competition"),
                                }
                            )
                        else:
                            st.warning("No volume data found")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with trends_col2:
        st.markdown("#### 📈 Google Trends")
        trends_keywords = st.text_input(
            "Enter keywords for trends (comma-separated):",
            key="trends_keywords_input",
            placeholder="seo tools, digital marketing"
        )
        time_range = st.selectbox(
            "Time Range",
            ["past_hour", "past_day", "past_7_days", "past_30_days", "past_90_days", "past_12_months", "past_5_years"],
            index=5
        )
        
        if st.button("Get Trends Data"):
            if trends_keywords:
                keywords_list = [kw.strip() for kw in trends_keywords.split(',') if kw.strip()]
                
                with st.spinner("🔄 Getting trends data..."):
                    try:
                        agent = KeywordAgent()
                        trends_data = agent.get_keyword_trends(keywords_list, country, time_range)
                        
                        if trends_data and trends_data.get('graph_data'):
                            st.success("✅ Retrieved trends data!")
                            
                            # Display trends chart
                            if trends_data.get('graph_data'):
                                chart_data = pd.DataFrame(trends_data['graph_data'])
                                st.line_chart(chart_data.set_index('date'))
                            
                            # Show related queries
                            if trends_data.get('related_queries'):
                                st.markdown("#### Related Queries")
                                for query in trends_data['related_queries'][:5]:
                                    st.write(f"• {query}")
                        else:
                            st.warning("No trends data found")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

with tab5:
    st.markdown("### 🔍 Content Analysis")
    
    content_url = st.text_input(
        "Enter URL to analyze:",
        key="content_url_input",
        placeholder="https://example.com/page"
    )
    
    enable_js = st.checkbox("Enable JavaScript", value=True)
    
    if st.button("Analyze Content", type="primary"):
        if content_url:
            with st.spinner("🔄 Analyzing content..."):
                try:
                    agent = KeywordAgent()
                    content_data = agent.analyze_content(content_url, enable_js)
                    
                    if content_data:
                        extraction_method = content_data.get('extraction_method', 'unknown')
                        has_additional = content_data.get('additional_metrics') == 'dataforseo'
                        
                        # Show extraction status
                        if extraction_method == 'trafilatura':
                            st.success("✅ **Content Successfully Analyzed!**")
                            if has_additional:
                                st.info("📊 Using Trafilatura extraction with additional DataForSEO metrics (load time, readability)")
                            elif content_data.get('protected_site'):
                                st.info("🔒 Site is Cloudflare-protected. Using Trafilatura extraction (performance metrics unavailable)")
                            else:
                                st.info("📄 Using Trafilatura extraction for content analysis")
                        elif extraction_method == 'dataforseo':
                            st.success("✅ **Content analysis complete!**")
                            st.info("📊 Using DataForSEO API for full metrics")
                        else:
                            st.warning("⚠️ Content extraction method unknown")
                        
                        # Display content metrics
                        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                        
                        with metrics_col1:
                            st.metric("OnPage Score", f"{content_data.get('onpage_score', 0):.1f}/100")
                        
                        with metrics_col2:
                            word_count = content_data.get('word_count', 0)
                            st.metric("Word Count", word_count)
                        
                        with metrics_col3:
                            load_time = content_data.get('load_time', 0)
                            st.metric("Load Time", f"{load_time}ms" if isinstance(load_time, (int, float)) else "N/A")
                        
                        with metrics_col4:
                            page_size = content_data.get('page_size', 0)
                            st.metric("Page Size", f"{page_size} bytes")
                        
                        # Additional metrics row
                        metrics2_col1, metrics2_col2, metrics2_col3, metrics2_col4 = st.columns(4)
                        
                        with metrics2_col1:
                            internal_links = content_data.get('internal_links', 0)
                            st.metric("Internal Links", internal_links)
                        
                        with metrics2_col2:
                            external_links = content_data.get('external_links', 0)
                            st.metric("External Links", external_links)
                        
                        with metrics2_col3:
                            images = content_data.get('images', 0)
                            st.metric("Images", images)
                        
                        with metrics2_col4:
                            readability = content_data.get('readability', {})
                            flesch_score = readability.get('flesch_kincaid', 0)
                            st.metric("Reading Score", f"{flesch_score:.1f}")
                        
                        # Content details
                        st.markdown("#### Content Structure")
                        
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            # Get title and description directly from content_data
                            title = content_data.get('title', 'N/A')
                            meta_desc = content_data.get('meta_description', 'N/A')
                            
                            # Display based on extraction method
                            extraction_method = content_data.get('extraction_method', '')
                            
                            st.markdown("**Title:**")
                            st.write(title if title else 'N/A')
                            if extraction_method == 'trafilatura':
                                st.caption("📄 Extracted via Trafilatura")
                            elif extraction_method == 'dataforseo':
                                st.caption("📊 From DataForSEO API")
                            
                            st.markdown("**Meta Description:**")
                            st.write(meta_desc if meta_desc else 'N/A')
                            
                            st.markdown("**H1 Tags:**")
                            for h1 in content_data.get('h1_tags', [])[:3]:
                                st.write(f"• {h1}")
                        
                        with detail_col2:
                            st.markdown("**H2 Tags:**")
                            for h2 in content_data.get('h2_tags', [])[:5]:
                                st.write(f"• {h2}")
                            
                            st.markdown("**H3 Tags:**")
                            for h3 in content_data.get('h3_tags', [])[:5]:
                                st.write(f"• {h3}")
                        
                        # SEO Checks
                        st.markdown("#### ✅ SEO Checks")
                        seo_checks = content_data.get('seo_checks', {})
                        api_checks = content_data.get('checks', {})
                        
                        check_col1, check_col2, check_col3, check_col4, check_col5 = st.columns(5)
                        
                        with check_col1:
                            status = "✅" if seo_checks.get('has_https') else "❌"
                            st.write(f"{status} HTTPS")
                        
                        with check_col2:
                            status = "✅" if seo_checks.get('has_title') else "❌"
                            st.write(f"{status} Title")
                        
                        with check_col3:
                            status = "✅" if seo_checks.get('has_description') else "❌"
                            st.write(f"{status} Meta Desc")
                        
                        with check_col4:
                            # Check for favicon in seo_checks first, then api_checks
                            has_favicon = seo_checks.get('has_favicon', False) or not api_checks.get('no_favicon', True)
                            status = "✅" if has_favicon else "❌"
                            st.write(f"{status} Favicon")
                        
                        with check_col5:
                            # Check for SEO friendly URL in seo_checks first, then api_checks
                            seo_friendly = seo_checks.get('seo_friendly_url', False) or api_checks.get('seo_friendly_url', False)
                            status = "✅" if seo_friendly else "❌"
                            st.write(f"{status} SEO URL")
                        
                        # AI Insights
                        st.markdown("#### 🤖 AI Optimization Insights")
                        
                        if content_data.get('ai_insights'):
                            with st.expander("📝 View Full Analysis", expanded=True):
                                # Display the AI insights
                                insights = content_data['ai_insights']
                                if insights:
                                    st.markdown(insights)
                                else:
                                    st.info("Generating insights...")
                        else:
                            # Generate insights if not available
                            with st.spinner("Generating AI insights..."):
                                from agents.keyword_agent import KeywordAgent
                                agent = KeywordAgent()
                                insights = agent._generate_content_insights(content_data)
                                if insights:
                                    with st.expander("📝 View Full Analysis", expanded=True):
                                        st.markdown(insights)
                                else:
                                    st.warning("Could not generate AI insights")
                    else:
                        st.warning("No content data found")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab6:
    st.markdown("### 📋 Reports & Analytics")
    
    st.markdown("#### 📊 Session Summary")
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        if st.session_state.keywords_data:
            total_keywords = len(st.session_state.keywords_data)
            avg_volume = sum(kw.get('search_volume', 0) for kw in st.session_state.keywords_data) // max(total_keywords, 1)
            st.metric("Keywords Researched", total_keywords)
            st.metric("Avg. Search Volume", f"{avg_volume:,}")
    
    with summary_col2:
        if st.session_state.serp_data:
            st.metric("SERP Results Analyzed", len(st.session_state.serp_data))
    
    with summary_col3:
        st.metric("API Calls Made", "Real DataForSEO MCP")
    
    # Export comprehensive report
    if st.session_state.keywords_data or st.session_state.serp_data:
        st.markdown("#### 📥 Export Options")
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("📊 Generate Summary Report"):
                # Create comprehensive report
                report_data = {
                    "keywords": st.session_state.keywords_data or [],
                    "serp_results": st.session_state.serp_data or [],
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "summary": {
                        "total_keywords": len(st.session_state.keywords_data or []),
                        "total_serp_results": len(st.session_state.serp_data or [])
                    }
                }
                
                st.download_button(
                    label="📥 Download JSON Report",
                    data=json.dumps(report_data, indent=2),
                    file_name=f"seo_analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with export_col2:
            if st.button("📈 Generate Excel Report"):
                # Create multi-sheet Excel report
                from utils.export import create_keyword_report
                
                if st.session_state.keywords_data:
                    report = create_keyword_report(
                        st.session_state.keywords_data,
                        seed_keyword,
                        {"country": country, "language": language}
                    )
                    st.json(report["summary"])

# Enhanced trend analysis has been moved to tab4

with tab7:
    st.markdown("### 📝 Content Brief Generator")
    st.markdown("Generate comprehensive content briefs based on keyword and SERP analysis")
    
    # Content brief generation section
    brief_col1, brief_col2 = st.columns([2, 1])
    
    with brief_col1:
        # Keyword selection
        st.markdown("#### 🎯 Select Keyword")
        
        # Get available keywords from session state
        available_keywords = []
        if st.session_state.keywords_data:
            available_keywords = [kw['keyword'] for kw in st.session_state.keywords_data]
        
        if available_keywords:
            selected_keyword = st.selectbox(
                "Choose a keyword to create content brief for:",
                options=available_keywords,
                help="Select from your researched keywords"
            )
        else:
            selected_keyword = st.text_input(
                "Enter a keyword:",
                key="content_brief_keyword_input",
                placeholder="e.g., best seo tools 2024"
            )
            st.info("💡 Tip: Research keywords in Tab 1 first for better results")
        
        # Target audience
        target_audience = st.text_input(
            "Target Audience",
            key="content_brief_audience_input",
            value="general",
            placeholder="e.g., small business owners, marketing professionals"
        )
        
        # Additional context
        content_type = st.selectbox(
            "Content Type",
            options=["Blog Post", "Landing Page", "Product Page", "Guide/Tutorial", "Comparison Article"],
            index=0
        )
        
        # Generate button
        if st.button("🚀 Generate Content Brief", type="primary"):
            if selected_keyword:
                with st.spinner("🔄 Generating comprehensive content brief..."):
                    try:
                        agent = KeywordAgent()
                        
                        # Get SERP data if not already available
                        serp_results = []
                        if st.session_state.serp_data:
                            # Use existing SERP data if available
                            serp_results = st.session_state.serp_data
                        else:
                            # Fetch fresh SERP data
                            serp_results = agent.analyze_serp(selected_keyword, country, language)
                        
                        # Generate content brief
                        brief = agent.llm_client.generate_content_brief(
                            keyword=selected_keyword,
                            serp_results=serp_results,
                            target_audience=target_audience
                        )
                        
                        # Store in session state
                        st.session_state.content_brief = {
                            'keyword': selected_keyword,
                            'audience': target_audience,
                            'type': content_type,
                            'brief': brief,
                            'timestamp': pd.Timestamp.now().isoformat()
                        }
                        
                        st.success("✅ Content brief generated successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating content brief: {str(e)}")
            else:
                st.warning("Please enter or select a keyword")
    
    with brief_col2:
        st.markdown("#### 💡 Brief Features")
        st.info("""
        **What's included:**
        - 📌 3 title suggestions
        - 📋 Key topics to cover
        - 🏗️ Content structure
        - 📏 Word count recommendation
        - 🎯 Unique angle suggestions
        - 📢 CTA recommendations
        """)
    
    # Display generated brief
    if 'content_brief' in st.session_state and st.session_state.content_brief:
        st.markdown("---")
        st.markdown("### 📄 Generated Content Brief")
        
        # Brief metadata
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        with meta_col1:
            st.metric("Keyword", st.session_state.content_brief['keyword'])
        with meta_col2:
            st.metric("Audience", st.session_state.content_brief['audience'])
        with meta_col3:
            st.metric("Content Type", st.session_state.content_brief['type'])
        
        # Display the brief
        with st.expander("📝 Full Content Brief", expanded=True):
            st.markdown(st.session_state.content_brief['brief'])
        
        # Export options
        st.markdown("#### 📥 Export Options")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            # Export as text
            st.download_button(
                label="📄 Download as Text",
                data=f"Content Brief for: {st.session_state.content_brief['keyword']}\n\n{st.session_state.content_brief['brief']}",
                file_name=f"content_brief_{st.session_state.content_brief['keyword'].replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        with export_col2:
            # Export as JSON
            st.download_button(
                label="📊 Download as JSON",
                data=json.dumps(st.session_state.content_brief, indent=2),
                file_name=f"content_brief_{st.session_state.content_brief['keyword'].replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

with tab8:
    st.markdown("### ✍️ AI Content Generator")
    st.markdown("Generate SEO-optimized content based on your content brief")
    
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = None
    
    # Create two columns for config/chat and content
    config_col, content_col = st.columns([1, 2])
    
    with config_col:
        st.markdown("#### 📋 Content Configuration")
        
        # Check if content brief exists
        has_brief = 'content_brief' in st.session_state and st.session_state.content_brief
        
        if has_brief:
            st.success(f"📝 Using brief for: {st.session_state.content_brief['keyword']}")
        else:
            st.warning("💡 Generate a content brief in Tab 7 first for better results")
        
        # Content Type Selection
        content_type = st.selectbox(
            "Content Type",
            options=["Blog Post", "Landing Page", "Product Page", "Guide/Tutorial", "Comparison Article"],
            help="Select the type of content to generate"
        )
        
        # Target Audience
        default_audience = st.session_state.content_brief.get('audience', 'general') if has_brief else 'general'
        target_audience = st.text_input(
            "Target Audience",
            key="content_generator_audience_input",
            value=default_audience,
            placeholder="e.g., small business owners, marketing professionals"
        )
        
        # Title Selection
        st.markdown("#### 📌 Content Title")
        title_options = []
        
        if has_brief and st.session_state.content_brief.get('brief'):
            # Extract title suggestions from brief
            brief_text = st.session_state.content_brief['brief']
            lines = brief_text.split('\n')
            for i, line in enumerate(lines):
                if 'title' in line.lower() and i + 1 < len(lines):
                    # Look for the next 3 lines after "title" mention
                    for j in range(1, min(4, len(lines) - i)):
                        next_line = lines[i + j].strip()
                        if next_line and not next_line.startswith('#'):
                            title_options.append(next_line.lstrip('- •123. '))
        
        if title_options:
            title_options.append("Custom Title")
            selected_title_option = st.selectbox("Select Title", title_options)
            
            if selected_title_option == "Custom Title":
                title = st.text_input("Enter Custom Title", key="custom_title_input", placeholder="Enter your title")
            else:
                title = selected_title_option
        else:
            title = st.text_input(
                "Content Title",
                key="content_generator_title_input",
                placeholder="Enter a compelling title for your content"
            )
        
        # Word Count
        word_count = st.slider(
            "Target Word Count",
            min_value=500,
            max_value=4000,
            value=1500,
            step=100,
            help="Approximate word count for the content"
        )
        
        # Initialize default values for advanced settings
        tone = "professional"
        readability = "intermediate"
        heading_structure = None
        
        # Advanced Content Settings
        with st.expander("🎯 Advanced Content Settings", expanded=False):
            # Humanization Settings
            st.markdown("#### 🎨 Content Tone & Style")
            
            tone_col1, tone_col2 = st.columns(2)
            with tone_col1:
                tone = st.selectbox(
                    "Writing Tone",
                    options=["professional", "conversational", "friendly", "expert", "casual", "persuasive"],
                    index=1,  # Default to conversational
                    key="content_tone",
                    help="Choose the tone that best matches your brand voice"
                )
            
            with tone_col2:
                readability = st.selectbox(
                    "Readability Level",
                    options=["simple", "intermediate", "advanced"],
                    index=1,  # Default to intermediate
                    key="content_readability",
                    help="Simple: 8th grade | Intermediate: 10th grade | Advanced: College level"
                )
            
            # Custom Heading Structure
            st.markdown("#### 📝 Custom Heading Structure")
            st.info("Control the exact number and keywords for headings in your content")
            
            heading_col1, heading_col2, heading_col3 = st.columns(3)
            
            with heading_col1:
                h1_count = st.number_input(
                    "H1 Headings",
                    min_value=1,
                    max_value=1,
                    value=1,
                    key="h1_count",
                    help="Usually just the title (1 H1 per page for SEO)"
                )
            
            with heading_col2:
                h2_count = st.number_input(
                    "H2 Sections",
                    min_value=2,
                    max_value=10,
                    value=4,
                    key="h2_count",
                    help="Main sections of your content"
                )
            
            with heading_col3:
                h3_count = st.number_input(
                    "H3 per H2",
                    min_value=0,
                    max_value=5,
                    value=2,
                    key="h3_count",
                    help="Subsections under each H2"
                )
            
            # Keywords for headings
            h2_keywords_input = st.text_input(
                "Keywords for H2 Headings (comma-separated)",
                key="h2_keywords",
                placeholder="e.g., benefits, features, how to, guide",
                help="These keywords will be incorporated into H2 headings"
            )
            
            h3_keywords_input = st.text_input(
                "Keywords for H3 Headings (comma-separated)",
                key="h3_keywords",
                placeholder="e.g., tips, examples, best practices, steps",
                help="These keywords will be incorporated into H3 headings"
            )
            
            # Process heading keywords
            h2_keywords = [kw.strip() for kw in h2_keywords_input.split(',') if kw.strip()] if h2_keywords_input else []
            h3_keywords = [kw.strip() for kw in h3_keywords_input.split(',') if kw.strip()] if h3_keywords_input else []
            
            # Create heading structure dictionary
            heading_structure = {
                "h1_count": h1_count,
                "h2_count": h2_count,
                "h3_count": h3_count,
                "h2_keywords": h2_keywords,
                "h3_keywords": h3_keywords
            }
            
            # Humanization Options
            st.markdown("#### ✨ Humanization Features")
            
            human_col1, human_col2 = st.columns(2)
            
            with human_col1:
                include_examples = st.checkbox(
                    "Include Real-World Examples",
                    value=True,
                    key="include_examples",
                    help="Add practical examples and case studies"
                )
                
                use_storytelling = st.checkbox(
                    "Use Storytelling Elements",
                    value=True,
                    key="use_storytelling",
                    help="Include narratives and personal touches"
                )
                
                add_questions = st.checkbox(
                    "Add Rhetorical Questions",
                    value=True,
                    key="add_questions",
                    help="Engage readers with thought-provoking questions"
                )
            
            with human_col2:
                use_contractions = st.checkbox(
                    "Use Natural Contractions",
                    value=True,
                    key="use_contractions",
                    help="Use it's, don't, you'll for conversational flow"
                )
                
                vary_sentences = st.checkbox(
                    "Vary Sentence Length",
                    value=True,
                    key="vary_sentences",
                    help="Mix short, medium, and long sentences naturally"
                )
                
                personal_pronouns = st.checkbox(
                    "Use Personal Pronouns",
                    value=True,
                    key="personal_pronouns",
                    help="Include I, you, we for connection"
                )
        
        # MCP Research Toggle
        use_mcp = st.checkbox(
            "🔍 Use Real-time SEO Data",
            value=True,
            help="Enhance content with current SERP and keyword data"
        )
        
        # Chat Interface
        st.markdown("#### 💬 Refinement Chat")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history[-5:]:  # Show last 5 messages
                if msg['role'] == 'user':
                    st.info(f"You: {msg['content']}")
                else:
                    st.success(f"AI: {msg['content']}")
        
        # Chat input
        user_input = st.text_area(
            "Additional instructions or refinements:",
            key="content_generator_chat_input",
            placeholder="e.g., 'Add more statistics', 'Make it more conversational', 'Include case studies'",
            height=100
        )
        
        # Action buttons
        button_col1, button_col2 = st.columns(2)
        
        with button_col1:
            if st.button("🚀 Generate Content", type="primary", disabled=not title):
                if title:
                    with st.spinner("✨ Generating content with AI..."):
                        try:
                            # Import the content generator
                            from agents.content_generator import ContentGeneratorAgent
                            generator = ContentGeneratorAgent()
                            
                            # Add user input to chat history if provided
                            if user_input:
                                st.session_state.chat_history.append({
                                    'role': 'user',
                                    'content': user_input
                                })
                            
                            # Get content brief
                            content_brief = st.session_state.content_brief if has_brief else {
                                'keyword': title,
                                'brief': f"Create {content_type} about {title}"
                            }
                            
                            # Generate content with advanced settings
                            result = generator.generate_content(
                                content_brief=content_brief,
                                content_type=content_type,
                                target_audience=target_audience,
                                title=title,
                                word_count=word_count,
                                chat_history=st.session_state.chat_history,
                                use_mcp_research=use_mcp,
                                heading_structure=heading_structure,
                                tone=tone,
                                readability_level=readability
                            )
                            
                            st.session_state.generated_content = result
                            # ALSO store as a separate key that might persist better
                            st.session_state['content_backup'] = result['content']
                            st.session_state['metadata_backup'] = result.get('metadata', {})
                            print(f"DEBUG: Content stored, length: {len(result.get('content', ''))}")
                            
                            # Add AI response to chat
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': f"Generated {result['metadata'].get('word_count', 0)} words of {content_type} content."
                            })
                            
                            st.success("✅ Content generated successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Generation error: {str(e)}")
                else:
                    st.warning("Please enter a title")
        
        with button_col2:
            if st.button("🔄 Refine Content") and st.session_state.generated_content and user_input:
                with st.spinner("🔧 Refining content..."):
                    try:
                        from agents.content_generator import ContentGeneratorAgent
                        generator = ContentGeneratorAgent()
                        
                        # Add refinement request to chat
                        st.session_state.chat_history.append({
                            'role': 'user',
                            'content': user_input
                        })
                        
                        # Refine the content with updated word count
                        refined_content = generator.refine_content(
                            current_content=st.session_state.generated_content['content'],
                            refinement_instruction=user_input,
                            keyword=st.session_state.content_brief.get('keyword', '') if has_brief else '',
                            target_word_count=word_count  # Pass the current slider value
                        )
                        
                        # Update the content and metadata
                        st.session_state.generated_content['content'] = refined_content
                        st.session_state.generated_content['metadata']['refined'] = True
                        st.session_state.generated_content['metadata']['word_count'] = len(refined_content.split())
                        
                        # Also update backup storage for DigitalOcean
                        st.session_state['content_backup'] = refined_content
                        st.session_state['metadata_backup'] = st.session_state.generated_content['metadata']
                        
                        # Add AI response with updated word count
                        new_word_count = len(refined_content.split())
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': f"Content refined. New word count: {new_word_count} words."
                        })
                        
                        st.success("✅ Content refined!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Refinement error: {str(e)}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with content_col:
        st.markdown("#### 📄 Generated Content")
        
        # Try multiple ways to get the content
        content_to_display = None
        if 'generated_content' in st.session_state and st.session_state.generated_content:
            content_to_display = st.session_state.generated_content
        elif 'content_backup' in st.session_state and st.session_state.content_backup:
            # Reconstruct from backup
            content_to_display = {
                'content': st.session_state.content_backup,
                'metadata': st.session_state.get('metadata_backup', {}),
                'research_data': {}
            }
        
        if content_to_display:
            # Display metadata
            meta = content_to_display.get('metadata', {})
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            
            with meta_col1:
                st.metric("Word Count", meta.get('word_count', 0))
            with meta_col2:
                st.metric("Content Type", meta.get('type', 'Unknown'))
            with meta_col3:
                research_status = "✅ Yes" if meta.get('research_used') else "❌ No"
                st.metric("SEO Research", research_status)
            
            # Display content in expandable section
            with st.expander("📝 Full Content", expanded=True):
                st.markdown(content_to_display['content'])
            
            # Show research data if available
            research_data = st.session_state.generated_content.get('research_data', {})
            if research_data:
                with st.expander("🔍 Research Data Used"):
                    if research_data.get('competitor_insights'):
                        st.markdown("**Competitor Insights:**")
                        for comp in research_data['competitor_insights']:
                            st.write(f"• {comp['title']}")
                    
                    if research_data.get('related_terms'):
                        st.markdown("**Related Keywords:**")
                        st.write(", ".join(research_data['related_terms']))
                    
                    if research_data.get('trending'):
                        st.markdown(f"**Trend Status:** {research_data['trending']}")
            
            # Improvement suggestions
            if st.button("💡 Get Improvement Suggestions"):
                with st.spinner("Analyzing content..."):
                    try:
                        from agents.content_generator import ContentGeneratorAgent
                        generator = ContentGeneratorAgent()
                        
                        suggestions = generator.suggest_improvements(
                            st.session_state.generated_content['content']
                        )
                        
                        st.markdown("### 💡 Suggested Improvements")
                        
                        # Display suggestions in an expandable section
                        with st.expander("View AI-Powered Content Optimization Suggestions", expanded=True):
                            if suggestions:
                                for i, suggestion in enumerate(suggestions, 1):
                                    # Add icon based on suggestion area
                                    if 'SEO' in suggestion:
                                        icon = "🔍"
                                    elif 'Readability' in suggestion:
                                        icon = "📖"
                                    elif 'Structure' in suggestion:
                                        icon = "🏗️"
                                    elif 'Call-to-action' in suggestion or 'CTA' in suggestion:
                                        icon = "🎯"
                                    elif 'audience' in suggestion.lower():
                                        icon = "👥"
                                    else:
                                        icon = "💡"
                                    
                                    st.markdown(f"{icon} **{suggestion}**")
                                    st.markdown("---")
                            else:
                                st.info("No specific suggestions available at this time.")
                    
                    except Exception as e:
                        st.error(f"Error getting suggestions: {str(e)}")
            
            # Export options
            st.markdown("#### 📥 Export Options")
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                # Export as Markdown
                st.download_button(
                    label="📝 Download Markdown",
                    data=st.session_state.generated_content['content'],
                    file_name=f"content_{title.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            
            with export_col2:
                # Export as Text
                text_content = st.session_state.generated_content['content'].replace('#', '').replace('*', '')
                st.download_button(
                    label="📄 Download Text",
                    data=text_content,
                    file_name=f"content_{title.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            
            with export_col3:
                # Export as HTML
                import markdown
                html_content = markdown.markdown(st.session_state.generated_content['content'])
                st.download_button(
                    label="🌐 Download HTML",
                    data=html_content,
                    file_name=f"content_{title.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
            
            # Humanize Ultra button
            st.markdown("#### 🤖 Advanced Humanization")
            
            # Check if content is already humanized
            is_humanized = st.session_state.generated_content.get('metadata', {}).get('humanized', False)
            
            if is_humanized:
                st.info("✅ This content has already been humanized")
            
            if st.button("🤖 Humanize Ultra", 
                        disabled=is_humanized,
                        help="Apply advanced humanization using chunk-based processing to maintain natural flow and readability"):
                
                # Store original content before humanization
                if 'original_before_humanize' not in st.session_state:
                    st.session_state.original_before_humanize = st.session_state.generated_content['content']
                
                with st.spinner("🔄 Humanizing content..."):
                    try:
                        from agents.content_generator import ContentGeneratorAgent
                        generator = ContentGeneratorAgent()
                        
                        # Get current content and word count
                        current_content = st.session_state.generated_content['content']
                        current_words = len(current_content.split())
                        
                        # Calculate chunks for progress display
                        num_chunks = math.ceil(current_words / 1000)
                        
                        # Create a progress placeholder
                        progress_placeholder = st.empty()
                        progress_placeholder.info(f"Processing {num_chunks} chunks of ~1000 words each...")
                        
                        # Humanize the content
                        humanized_result = generator.humanize_ultra(
                            content=current_content,
                            target_word_count=current_words
                        )
                        
                        # Update content and metadata
                        st.session_state.generated_content['content'] = humanized_result['content']
                        st.session_state.generated_content['metadata'].update(humanized_result['metadata'])
                        
                        # Also update backup storage
                        st.session_state['content_backup'] = humanized_result['content']
                        st.session_state['metadata_backup'] = st.session_state.generated_content['metadata']
                        
                        # Clear progress and show success
                        progress_placeholder.empty()
                        
                        # Show humanization stats
                        meta = humanized_result['metadata']
                        st.success(f"""✅ Humanization Complete!
                        - Original: {meta['original_words']} words
                        - Humanized: {meta['final_words']} words
                        - Accuracy: {meta['accuracy_percentage']}%
                        - Chunks processed: {meta['chunks_processed']}
                        {"- Content expanded to maintain length" if meta['expanded'] else ""}""")
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': f"Content humanized successfully. Final word count: {meta['final_words']} words ({meta['accuracy_percentage']}% of target)."
                        })
                        
                        # Force a rerun to update the display
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Humanization error: {str(e)}")
            
            # Option to restore original (only show if content has been humanized)
            if is_humanized and 'original_before_humanize' in st.session_state:
                if st.button("↩️ Restore Original", help="Revert to the original non-humanized content"):
                    st.session_state.generated_content['content'] = st.session_state.original_before_humanize
                    st.session_state.generated_content['metadata']['humanized'] = False
                    st.session_state['content_backup'] = st.session_state.original_before_humanize
                    
                    # Recalculate word count
                    original_words = len(st.session_state.original_before_humanize.split())
                    st.session_state.generated_content['metadata']['word_count'] = original_words
                    st.session_state['metadata_backup'] = st.session_state.generated_content['metadata']
                    
                    st.success("✅ Original content restored")
                    st.rerun()
        else:
            st.info("👆 Configure your content settings and click 'Generate Content' to begin")
            
            # Show tips
            with st.expander("💡 Tips for Better Content"):
                st.markdown("""
                **For Best Results:**
                1. Generate a content brief first (Tab 7) for comprehensive guidance
                2. Use real-time SEO data for competitive insights
                3. Be specific with your target audience
                4. Use the chat to refine and improve the content
                5. Review improvement suggestions after generation
                
                **Content Types:**
                - **Blog Post:** Informative articles with SEO focus
                - **Landing Page:** Conversion-focused content
                - **Product Page:** Feature and benefit-driven content
                - **Guide/Tutorial:** Step-by-step instructional content
                - **Comparison Article:** Side-by-side analysis content
                """)

# Tab 9: Domain Analytics & Traffic Tracking
with tab9:
    st.header("🌐 Domain Analytics & Traffic Tracking")
    st.markdown("Track your website's keyword rankings, positions, and estimated traffic")
    
    # Input section
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        domain_input = st.text_input(
            "Enter Domain",
            placeholder="example.com or https://example.com",
            key="domain_analytics_input",
            help="Enter your domain to analyze keyword rankings and traffic"
        )
    
    with col2:
        country_domain = st.selectbox(
            "Country",
            options=["us", "uk", "au", "ca", "in", "de", "fr", "es", "it", "jp"],
            format_func=lambda x: {"us": "🇺🇸 United States", "uk": "🇬🇧 United Kingdom", 
                                  "au": "🇦🇺 Australia", "ca": "🇨🇦 Canada", "in": "🇮🇳 India",
                                  "de": "🇩🇪 Germany", "fr": "🇫🇷 France", "es": "🇪🇸 Spain",
                                  "it": "🇮🇹 Italy", "jp": "🇯🇵 Japan"}.get(x, x),
            key="domain_country"
        )
    
    with col3:
        analyze_domain_btn = st.button("🔍 Analyze Domain", type="primary", key="analyze_domain_btn")
    
    # Additional settings
    with st.expander("⚙️ Advanced Settings"):
        col1_adv, col2_adv = st.columns(2)
        with col1_adv:
            domain_limit = st.number_input(
                "Max Keywords to Analyze",
                min_value=10,
                max_value=500,
                value=100,
                step=50,
                key="domain_limit"
            )
        with col2_adv:
            language_domain = st.selectbox(
                "Language",
                options=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh"],
                format_func=lambda x: {"en": "English", "es": "Spanish", "fr": "French",
                                      "de": "German", "it": "Italian", "pt": "Portuguese",
                                      "ru": "Russian", "ja": "Japanese", "zh": "Chinese"}.get(x, x),
                key="domain_language"
            )
    
    # Process domain analysis
    if analyze_domain_btn and domain_input:
        with st.spinner(f"🔍 Analyzing domain: {domain_input}..."):
            try:
                # Initialize agent
                from agents.keyword_agent import KeywordAgent
                agent = KeywordAgent()
                
                # Get domain analytics
                domain_data = agent.analyze_domain_rankings(
                    domain=domain_input,
                    country=country_domain,
                    language=language_domain,
                    limit=domain_limit
                )
                
                if domain_data and domain_data.get('total_keywords', 0) > 0:
                    st.success(f"✅ Analysis complete! Found {domain_data['total_keywords']} keywords")
                    
                    # Store in session state
                    st.session_state.domain_data = domain_data
                    
                    # Overview Metrics
                    st.markdown("### 📊 Domain Overview")
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    
                    with metric_col1:
                        st.metric(
                            "Total Keywords",
                            f"{domain_data['total_keywords']:,}",
                            help="Total keywords your domain is ranking for"
                        )
                    
                    with metric_col2:
                        st.metric(
                            "Est. Monthly Traffic",
                            f"{domain_data['total_traffic']:,.0f}",
                            help="Estimated monthly organic traffic from all keywords"
                        )
                    
                    with metric_col3:
                        st.metric(
                            "Avg. Position",
                            f"{domain_data['avg_position']:.1f}",
                            help="Average ranking position across all keywords"
                        )
                    
                    with metric_col4:
                        st.metric(
                            "Total Search Volume",
                            f"{domain_data['total_search_volume']:,}",
                            help="Combined monthly search volume for all keywords"
                        )
                    
                    # Position Distribution
                    st.markdown("### 📈 Position Distribution")
                    pos_col1, pos_col2, pos_col3, pos_col4, pos_col5 = st.columns(5)
                    
                    overview = domain_data.get('overview', {})
                    with pos_col1:
                        st.metric("Top 3", overview.get('top_3_count', 0))
                    with pos_col2:
                        st.metric("Top 10", overview.get('top_10_count', 0))
                    with pos_col3:
                        st.metric("Pos 11-20", overview.get('positions_11_20', 0))
                    with pos_col4:
                        st.metric("Pos 21-50", overview.get('positions_21_50', 0))
                    with pos_col5:
                        st.metric("Pos 50+", overview.get('positions_50_plus', 0))
                    
                    # Create two columns for side-by-side display
                    left_col, right_col = st.columns(2)
                    
                    with left_col:
                        # Top Traffic Keywords
                        st.markdown("### 🎯 Top Traffic-Driving Keywords")
                        top_traffic = domain_data.get('top_traffic_keywords', [])
                        if top_traffic:
                            traffic_data = []
                            for kw in top_traffic[:10]:
                                traffic_data.append({
                                    "Keyword": kw.get('keyword', ''),
                                    "Position": kw.get('position', 0),
                                    "Est. Traffic": f"{kw.get('etv', 0):.1f}",
                                    "Volume": f"{kw.get('search_volume', 0):,}",
                                    "Difficulty": kw.get('difficulty', 0)
                                })
                            
                            traffic_df = pd.DataFrame(traffic_data)
                            st.dataframe(traffic_df, use_container_width=True, hide_index=True)
                    
                    with right_col:
                        # Quick Wins
                        st.markdown("### 🚀 Quick Win Opportunities")
                        st.markdown("*Keywords ranking 11-20 with good traffic potential*")
                        quick_wins = domain_data.get('quick_wins', [])
                        if quick_wins:
                            qw_data = []
                            for kw in quick_wins[:10]:
                                qw_data.append({
                                    "Keyword": kw.get('keyword', ''),
                                    "Position": kw.get('position', 0),
                                    "Volume": f"{kw.get('search_volume', 0):,}",
                                    "Potential": f"+{kw.get('etv', 0):.0f}",
                                    "Difficulty": kw.get('difficulty', 0)
                                })
                            
                            qw_df = pd.DataFrame(qw_data)
                            st.dataframe(qw_df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No quick win opportunities found (keywords ranking 11-20)")
                    
                    # AI Insights
                    insights = domain_data.get('insights', {})
                    if insights:
                        st.markdown("### 💡 SEO Insights & Recommendations")
                        
                        # Display insights in columns
                        insight_col1, insight_col2 = st.columns(2)
                        
                        with insight_col1:
                            if insights.get('strengths'):
                                st.markdown("**✅ Strengths:**")
                                for strength in insights['strengths']:
                                    st.markdown(f"• {strength}")
                            
                            if insights.get('opportunities'):
                                st.markdown("**🎯 Opportunities:**")
                                for opp in insights['opportunities']:
                                    st.markdown(f"• {opp}")
                        
                        with insight_col2:
                            if insights.get('recommendations'):
                                st.markdown("**📋 Recommendations:**")
                                for rec in insights['recommendations']:
                                    st.markdown(f"• {rec}")
                        
                        # AI recommendations if available
                        if insights.get('ai_recommendations'):
                            st.markdown("**🤖 AI-Powered Analysis:**")
                            # Use an expander for long AI analysis
                            with st.expander("View Detailed AI Recommendations", expanded=True):
                                st.markdown(insights['ai_recommendations'])
                    
                    # Full Keywords Table
                    st.markdown("### 📋 All Ranking Keywords")
                    
                    # Filtering options
                    filter_col1, filter_col2, filter_col3 = st.columns(3)
                    
                    with filter_col1:
                        pos_filter = st.selectbox(
                            "Filter by Position",
                            ["All", "Top 10", "11-20", "21-50", "50+"],
                            key="domain_pos_filter"
                        )
                    
                    with filter_col2:
                        vol_filter = st.number_input(
                            "Min. Search Volume",
                            min_value=0,
                            value=0,
                            step=100,
                            key="domain_vol_filter"
                        )
                    
                    with filter_col3:
                        sort_by = st.selectbox(
                            "Sort by",
                            ["Traffic (High to Low)", "Position (Best First)", "Volume (High to Low)", "Keyword (A-Z)"],
                            key="domain_sort"
                        )
                    
                    # Apply filters
                    keywords_list = domain_data.get('keywords', [])
                    filtered_keywords = keywords_list.copy()
                    
                    # Position filter
                    if pos_filter == "Top 10":
                        filtered_keywords = [k for k in filtered_keywords if k.get('position', 0) <= 10]
                    elif pos_filter == "11-20":
                        filtered_keywords = [k for k in filtered_keywords if 11 <= k.get('position', 0) <= 20]
                    elif pos_filter == "21-50":
                        filtered_keywords = [k for k in filtered_keywords if 21 <= k.get('position', 0) <= 50]
                    elif pos_filter == "50+":
                        filtered_keywords = [k for k in filtered_keywords if k.get('position', 0) > 50]
                    
                    # Volume filter
                    filtered_keywords = [k for k in filtered_keywords if k.get('search_volume', 0) >= vol_filter]
                    
                    # Sort
                    if sort_by == "Traffic (High to Low)":
                        filtered_keywords.sort(key=lambda x: x.get('etv', 0), reverse=True)
                    elif sort_by == "Position (Best First)":
                        filtered_keywords.sort(key=lambda x: x.get('position', 999))
                    elif sort_by == "Volume (High to Low)":
                        filtered_keywords.sort(key=lambda x: x.get('search_volume', 0), reverse=True)
                    else:  # Alphabetical
                        filtered_keywords.sort(key=lambda x: x.get('keyword', ''))
                    
                    # Create DataFrame for display
                    if filtered_keywords:
                        display_data = []
                        for kw in filtered_keywords:
                            display_data.append({
                                "Keyword": kw.get('keyword', ''),
                                "Position": kw.get('position', 0),
                                "Est. Traffic": f"{kw.get('etv', 0):.1f}",
                                "Search Volume": f"{kw.get('search_volume', 0):,}",
                                "CPC": f"${kw.get('cpc', 0):.2f}",
                                "Difficulty": kw.get('difficulty', 0),
                                "URL": kw.get('url', '')
                            })
                        
                        results_df = pd.DataFrame(display_data)
                        
                        # Display with pagination
                        st.markdown(f"**Showing {len(filtered_keywords)} keywords**")
                        st.dataframe(
                            results_df,
                            use_container_width=True,
                            hide_index=True,
                            height=400
                        )
                        
                        # Export options
                        st.markdown("### 📥 Export Results")
                        export_col1, export_col2 = st.columns(2)
                        
                        with export_col1:
                            # CSV export
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📊 Download CSV",
                                data=csv,
                                file_name=f"domain_analytics_{domain_input.replace('.', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
                        
                        with export_col2:
                            # JSON export
                            json_data = json.dumps(domain_data, indent=2)
                            st.download_button(
                                label="📋 Download Full Report (JSON)",
                                data=json_data,
                                file_name=f"domain_report_{domain_input.replace('.', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.json",
                                mime="application/json"
                            )
                    else:
                        st.info("No keywords found matching your filters")
                    
                else:
                    st.warning(f"No ranking data found for {domain_input}. Make sure the domain is correct and has organic rankings.")
                    
            except Exception as e:
                st.error(f"❌ Error analyzing domain: {str(e)}")
                st.info("Please check your domain and try again. Make sure DataForSEO credentials are configured.")
    
    elif analyze_domain_btn:
        st.warning("Please enter a domain to analyze")
    
    else:
        # Instructions and features
        st.markdown("""
        ### 🎯 Features
        
        This powerful domain analytics tool provides:
        
        **📊 Comprehensive Metrics:**
        - Total keywords your site ranks for
        - Estimated monthly organic traffic
        - Average ranking position
        - Position distribution analysis
        
        **🚀 Traffic Insights:**
        - Top traffic-driving keywords
        - Quick win opportunities (keywords close to page 1)
        - Keyword difficulty analysis
        - Search volume and CPC data
        
        **💡 Smart Recommendations:**
        - AI-powered SEO insights
        - Actionable optimization suggestions
        - Competitive positioning analysis
        
        **📥 Export Options:**
        - CSV export for spreadsheet analysis
        - JSON export for complete data
        
        ### 📖 How to Use
        
        1. **Enter your domain** (e.g., example.com)
        2. **Select country and language** for localized results
        3. **Click "Analyze Domain"** to get comprehensive insights
        4. **Review the data** to identify optimization opportunities
        5. **Export results** for further analysis
        
        ### 💡 Pro Tips
        
        - **Quick Wins**: Focus on keywords ranking 11-20 for fastest improvements
        - **Traffic Value**: Sort by ETV to find your most valuable keywords
        - **Content Gaps**: Keywords with high volume but low rankings are content opportunities
        - **Regular Monitoring**: Track your progress by analyzing weekly or monthly
        """)

# Sidebar
with st.sidebar:
    st.markdown("### 🛠️ Settings")
    
    # API Status
    st.markdown("#### API Status")
    if os.getenv("DATAFORSEO_USERNAME") and os.getenv("DATAFORSEO_PASSWORD"):
        st.success("✅ DataForSEO Connected")
    else:
        st.error("❌ DataForSEO Not Connected")
    
    if os.getenv("OPENROUTER_API_KEY"):
        st.success("✅ OpenRouter Connected")
    else:
        st.error("❌ OpenRouter Not Connected")
    
    # Model selection
    st.markdown("#### LLM Model")
    model = st.selectbox(
        "Select Model",
        options=[
            "google/gemini-2.5-flash-lite",
            "anthropic/claude-3-haiku",
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.2-3b-instruct"
        ],
        index=0
    )
    
    # About
    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
    **BMM SEO Agent** is an intelligent keyword research tool that combines:
    - 🔍 DataForSEO for real-time data
    - 🤖 AI-powered analysis
    - 📊 Advanced filtering
    - 📥 Easy export options
    """)