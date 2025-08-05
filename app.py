import streamlit as st
import pandas as pd
from agents.keyword_agent import KeywordAgent
from utils.export import export_to_csv, export_to_excel
import os
import json
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🔑 Keyword Research", 
    "📊 SERP Analysis", 
    "🏆 Competitor Analysis",
    "📈 Trends & Volume",
    "🔍 Content Analysis",
    "📋 Reports",
    "📝 Content Brief",
    "✍️ Content Generator"
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
                        competitor_keywords = agent.analyze_competitor_keywords(clean_domain, country, language, 20)
                        
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
                        st.success("✅ Content analysis complete!")
                        
                        # Display content metrics
                        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                        
                        with metrics_col1:
                            st.metric("OnPage Score", f"{content_data.get('onpage_score', 0):.1f}/100")
                        
                        with metrics_col2:
                            st.metric("Word Count", content_data.get('word_count', 0))
                        
                        with metrics_col3:
                            st.metric("Load Time", f"{content_data.get('load_time', 0)}ms")
                        
                        with metrics_col4:
                            st.metric("Page Size", f"{content_data.get('page_size', 0)} bytes")
                        
                        # Additional metrics row
                        metrics2_col1, metrics2_col2, metrics2_col3, metrics2_col4 = st.columns(4)
                        
                        with metrics2_col1:
                            st.metric("Internal Links", content_data.get('internal_links', 0))
                        
                        with metrics2_col2:
                            st.metric("External Links", content_data.get('external_links', 0))
                        
                        with metrics2_col3:
                            st.metric("Images", content_data.get('images', 0))
                        
                        with metrics2_col4:
                            readability = content_data.get('readability', {})
                            st.metric("Reading Score", f"{readability.get('flesch_kincaid', 0):.1f}")
                        
                        # Content details
                        st.markdown("#### Content Structure")
                        
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            st.markdown("**Title:**")
                            st.write(content_data.get('title', 'N/A'))
                            
                            st.markdown("**Meta Description:**")
                            st.write(content_data.get('meta_description', 'N/A'))
                            
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
                            status = "✅" if seo_checks.get('has_favicon') else "❌"
                            st.write(f"{status} Favicon")
                        
                        with check_col5:
                            status = "✅" if seo_checks.get('seo_friendly_url') else "❌"
                            st.write(f"{status} SEO URL")
                        
                        # AI Insights
                        if content_data.get('ai_insights'):
                            st.markdown("#### 🤖 AI Optimization Insights")
                            with st.expander("📝 View Full Analysis", expanded=True):
                                st.markdown(content_data['ai_insights'])
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
                            
                            # Generate content
                            result = generator.generate_content(
                                content_brief=content_brief,
                                content_type=content_type,
                                target_audience=target_audience,
                                title=title,
                                word_count=word_count,
                                chat_history=st.session_state.chat_history,
                                use_mcp_research=use_mcp
                            )
                            
                            st.session_state.generated_content = result
                            
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
                        
                        # Refine the content
                        refined_content = generator.refine_content(
                            current_content=st.session_state.generated_content['content'],
                            refinement_instruction=user_input,
                            keyword=st.session_state.content_brief.get('keyword', '') if has_brief else ''
                        )
                        
                        # Update the content
                        st.session_state.generated_content['content'] = refined_content
                        st.session_state.generated_content['metadata']['refined'] = True
                        
                        # Add AI response
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': "Content refined based on your instructions."
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
        
        if st.session_state.generated_content:
            # Display metadata
            meta = st.session_state.generated_content.get('metadata', {})
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
                st.markdown(st.session_state.generated_content['content'])
            
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