import os
from typing import List, Dict, Any
from utils.llm_client import LLMClient
from mcp.client import DataForSEOMCP
import time
import json

class KeywordAgent:
    """
    BMM SEO Agent for keyword research using DataForSEO MCP integration and LLM analysis
    """
    
    def __init__(self):
        # Initialize MCP client for DataForSEO
        self.dataforseo_mcp = DataForSEOMCP()
        
        # Keep compatibility reference
        self.dataforseo_client = self.dataforseo_mcp
        
        # Initialize LLM client
        self.llm_client = LLMClient()
        
        print("✅ KeywordAgent initialized with DataForSEO MCP integration")
        print("📊 Available capabilities: Keyword Research, SERP Analysis, Competitor Analysis, Content Analysis, Trends")
    
    
    def research_keywords(
        self,
        seed_keyword: str,
        country: str = "us",
        language: str = "en",
        min_volume: int = 100,
        max_difficulty: int = 70,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Research keywords using DataForSEO MCP
        """
        try:
            print(f"🔍 Researching keywords for: {seed_keyword}")
            
            # Convert country/language codes to full names for MCP
            location = self._get_location_name(country)
            language_name = self._get_language_name(language)
            
            # Get keywords via MCP
            keywords = self.dataforseo_mcp.get_keyword_suggestions(
                seed_keyword=seed_keyword,
                location=location,
                language=language_name,
                limit=limit
            )
            
            print(f"📊 Retrieved {len(keywords)} keywords from MCP")
            
            # Apply filters
            filtered_keywords = []
            for kw in keywords:
                if (kw.get("search_volume", 0) >= min_volume and 
                    kw.get("difficulty", 0) <= max_difficulty):
                    filtered_keywords.append(kw)
            
            print(f"✅ {len(filtered_keywords)} keywords passed filters")
            
            # Add AI insights
            enhanced_keywords = self._enhance_with_ai_insights(filtered_keywords, seed_keyword)
            
            return enhanced_keywords
            
        except Exception as e:
            print(f"❌ MCP Error: {str(e)}")
            raise
    
    def analyze_serp(
        self,
        keyword: str,
        country: str = "us",
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Analyze SERP results using DataForSEO MCP
        """
        try:
            print(f"🔍 Analyzing SERP for: {keyword}")
            
            # Convert country/language codes to full names for MCP
            location = self._get_location_name(country)
            language_name = self._get_language_name(language)
            
            # Get SERP data via MCP
            serp_results = self.dataforseo_mcp.get_serp_analysis(
                keyword=keyword,
                location=location,
                language=language_name
            )
            
            print(f"📊 Retrieved {len(serp_results)} SERP results from MCP")
            
            # Add AI insights for content gaps
            for result in serp_results:
                result["insights"] = self._analyze_content_gap(result, keyword)
            
            return serp_results
            
        except Exception as e:
            print(f"❌ SERP MCP Error: {str(e)}")
            raise
    
    def analyze_competitor_keywords(
        self,
        target_domain: str,
        country: str = "us",
        language: str = "en",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Analyze keywords that a competitor domain is ranking for
        """
        try:
            print(f"🔍 Analyzing competitor keywords for: {target_domain}")
            
            location = self._get_location_name(country)
            language_name = self._get_language_name(language)
            
            # Get ranked keywords via REST API (only accepts domain and limit)
            keywords = self.dataforseo_mcp.get_ranked_keywords(
                target_domain=target_domain,
                limit=limit
            )
            
            print(f"📊 Retrieved {len(keywords)} competitor keywords from MCP")
            
            return keywords
            
        except Exception as e:
            print(f"❌ Competitor Keywords MCP Error: {str(e)}")
            return []
    
    def analyze_competitor_domains(
        self,
        target_domain: str,
        country: str = "us",
        language: str = "en",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find competitor domains for a target domain
        """
        try:
            print(f"🔍 Finding competitors for: {target_domain}")
            
            location = self._get_location_name(country)
            language_name = self._get_language_name(language)
            
            # Get competitor domains via REST API
            competitors = self.dataforseo_mcp.get_competitor_domains(
                target_domain=target_domain,
                location=location,
                language=language_name
            )
            
            print(f"📊 Retrieved {len(competitors)} competitor domains from MCP")
            
            return competitors
            
        except Exception as e:
            print(f"❌ Competitor Domains MCP Error: {str(e)}")
            return []
    
    def get_search_volume_trends(
        self,
        keywords: List[str],
        country: str = "us",
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Get detailed search volume data for specific keywords
        """
        try:
            print(f"📈 Getting search volume data for {len(keywords)} keywords")
            
            location = self._get_location_name(country)
            language_name = self._get_language_name(language)
            
            # Get search volume data via MCP
            volume_data = self.dataforseo_mcp.get_search_volume_data(
                keywords=keywords,
                location=location,
                language=language_name
            )
            
            print(f"📊 Retrieved search volume data for {len(volume_data)} keywords from MCP")
            
            return volume_data
            
        except Exception as e:
            print(f"❌ Search Volume MCP Error: {str(e)}")
            return []
    
    def get_keyword_trends(
        self,
        keywords: List[str],
        country: str = "us",
        time_range: str = "past_12_months"
    ) -> Dict[str, Any]:
        """
        Get Google Trends data for keywords
        """
        try:
            print(f"📈 Getting trends data for {len(keywords)} keywords")
            
            location = self._get_location_name(country)
            
            # Get trends data via MCP
            trends_data = self.dataforseo_mcp.get_trends_data(
                keywords=keywords,
                location=location,
                time_range=time_range
            )
            
            print(f"📊 Retrieved trends data from MCP")
            
            return trends_data
            
        except Exception as e:
            print(f"❌ Trends MCP Error: {str(e)}")
            return {}
    
    def analyze_content(
        self,
        url: str,
        enable_javascript: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze on-page content of a URL
        """
        try:
            print(f"🔍 Analyzing content for: {url}")
            
            # Get content analysis via MCP
            content_data = self.dataforseo_mcp.get_content_analysis(url=url)
            
            print(f"📊 Retrieved content analysis from MCP")
            
            # Add AI insights for content optimization
            if content_data:
                content_data["ai_insights"] = self._generate_content_insights(content_data)
            
            return content_data
            
        except Exception as e:
            print(f"❌ Content Analysis MCP Error: {str(e)}")
            return {}
    
    def _generate_content_insights(self, content_data: Dict) -> str:
        """Generate AI insights for content optimization"""
        try:
            prompt = f"""
            Analyze this website content data and provide comprehensive SEO optimization insights:

            **Page Details:**
            - Title: {content_data.get('title', 'N/A')}
            - Meta Description: {content_data.get('meta_description', 'N/A')}
            - URL: {content_data.get('url', 'N/A')}
            - OnPage Score: {content_data.get('onpage_score', 0)}/100

            **Content Metrics:**
            - Word Count: {content_data.get('word_count', 0)}
            - H1 Tags: {len(content_data.get('h1_tags', []))} 
            - H2 Tags: {len(content_data.get('h2_tags', []))} ({content_data.get('h2_tags', [])})
            - H3 Tags: {len(content_data.get('h3_tags', []))}
            - Internal Links: {content_data.get('internal_links', 0)}
            - External Links: {content_data.get('external_links', 0)}
            - Images: {content_data.get('images', 0)}

            **Technical SEO:**
            - Page Load Time: {content_data.get('load_time', 0)}ms
            - Page Size: {content_data.get('page_size', 0)} bytes
            - HTTPS: {'Yes' if content_data.get('seo_checks', {}).get('has_https') else 'No'}

            Please provide:
            1. **Analysis Summary** - Overall assessment of the page's SEO health
            2. **Critical Issues** - High-priority problems that need immediate attention
            3. **Optimization Recommendations** - 5-7 specific, actionable improvements
            4. **Content Strategy** - Suggestions for content enhancement
            5. **Technical Improvements** - Performance and technical SEO recommendations

            Format your response with clear headers and bullet points for readability.
            """
            
            return self.llm_client.generate_text(prompt, max_tokens=1500, temperature=0.3)
            
        except Exception:
            return "Content analysis complete. Consider optimizing title tags, meta descriptions, and heading structure for better SEO performance."
    
    def _get_location_name(self, country: str) -> str:
        """Convert country code to full name for MCP"""
        location_names = {
            "us": "United States",
            "uk": "United Kingdom", 
            "ca": "Canada",
            "au": "Australia",
            "in": "India",
            "de": "Germany",
            "fr": "France",
            "es": "Spain",
            "br": "Brazil",
            "jp": "Japan"
        }
        return location_names.get(country, "United States")
    
    def _get_language_name(self, language: str) -> str:
        """Convert language code to full name for MCP"""
        language_names = {
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
        }
        return language_names.get(language, "English")
    
    def _classify_keyword_type(self, keyword: str, seed_keyword: str) -> str:
        """Classify keyword type based on structure"""
        keyword_lower = keyword.lower()
        seed_lower = seed_keyword.lower()
        
        # Question keywords
        if any(q in keyword_lower for q in ["what", "how", "why", "when", "where", "which", "who"]):
            return "Question"
        
        # Comparison keywords
        if any(c in keyword_lower for c in ["vs", "versus", "compare", "best", "top"]):
            return "Comparison"
        
        # Long-tail keywords (4+ words)
        if len(keyword.split()) >= 4:
            return "Long-tail"
        
        # Branded keywords
        if seed_lower in keyword_lower and keyword_lower != seed_lower:
            return "Related"
        
        return "Generic"
    
    def _enhance_with_ai_insights(self, keywords: List[Dict], seed_keyword: str) -> List[Dict]:
        """Enhance keywords with AI-generated insights"""
        try:
            # Prepare prompt for keyword analysis
            keywords_text = "\n".join([f"- {kw['keyword']} (Volume: {kw['search_volume']}, Difficulty: {kw['difficulty']})" for kw in keywords[:10]])
            
            prompt = f"""
            Analyze these keywords for "{seed_keyword}" and provide brief insights:
            
            {keywords_text}
            
            For each keyword, provide a one-sentence insight about:
            1. Content opportunity
            2. User intent
            3. Competition level
            
            Format as JSON array with keyword and insight fields.
            """
            
            # Get AI insights
            ai_response = self.llm_client.generate_text(prompt)
            
            # Parse and match insights (simplified for now)
            for keyword in keywords:
                keyword["ai_insight"] = f"Keyword '{keyword['keyword']}' shows {self._get_difficulty_level(keyword['difficulty'])} competition with good content opportunity."
            
            return keywords
            
        except Exception as e:
            # Return keywords without AI insights
            return keywords
    
    def _analyze_content_gap(self, serp_result: Dict, keyword: str) -> str:
        """Analyze content gaps for SERP result"""
        try:
            prompt = f"""
            Analyze this SERP result for keyword "{keyword}":
            
            Title: {serp_result.get('title', '')}
            Description: {serp_result.get('description', '')}
            URL: {serp_result.get('url', '')}
            
            Provide a brief content gap analysis in one sentence.
            """
            
            return self.llm_client.generate_text(prompt)
            
        except Exception:
            return f"Content opportunity: Consider creating comprehensive content about {keyword} targeting this search intent."
    
    def _get_difficulty_level(self, difficulty: int) -> str:
        """Convert difficulty score to level"""
        if difficulty < 30:
            return "low"
        elif difficulty < 70:
            return "medium"
        else:
            return "high"
    
    def analyze_domain_rankings(
        self,
        domain: str,
        country: str = "us",
        language: str = "en",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze domain's keyword rankings and traffic
        
        Returns comprehensive domain analytics including:
        - Total keywords ranking
        - Total estimated traffic 
        - Position distribution
        - Top traffic keywords
        - Quick win opportunities
        """
        try:
            print(f"🔍 Analyzing domain rankings for: {domain}")
            
            # Clean domain (remove protocol if present)
            if domain.startswith(('http://', 'https://')):
                domain = domain.split('://')[1]
            if domain.endswith('/'):
                domain = domain[:-1]
            
            # Get country and language names
            country_name = self._get_location_name(country)
            language_name = self._get_language_name(language)
            
            # Get ranked keywords with traffic data
            keywords = self.dataforseo_mcp.get_ranked_keywords(
                target_domain=domain,
                location=country_name,
                language=language_name,
                limit=limit
            )
            
            if not keywords:
                return {
                    "domain": domain,
                    "total_keywords": 0,
                    "total_traffic": 0,
                    "avg_position": 0,
                    "keywords": [],
                    "overview": {},
                    "insights": {}
                }
            
            # Calculate metrics
            total_traffic = sum(kw.get('etv', 0) for kw in keywords)
            total_search_volume = sum(kw.get('search_volume', 0) for kw in keywords)
            avg_position = sum(kw.get('position', 0) for kw in keywords) / len(keywords) if keywords else 0
            
            # Position distribution
            position_ranges = {
                "top_3": [],
                "top_10": [],
                "positions_11_20": [],
                "positions_21_50": [],
                "positions_50_plus": []
            }
            
            for kw in keywords:
                pos = kw.get('position', 0)
                if pos <= 3:
                    position_ranges["top_3"].append(kw)
                elif pos <= 10:
                    position_ranges["top_10"].append(kw)
                elif pos <= 20:
                    position_ranges["positions_11_20"].append(kw)
                elif pos <= 50:
                    position_ranges["positions_21_50"].append(kw)
                else:
                    position_ranges["positions_50_plus"].append(kw)
            
            # Sort keywords by traffic value
            keywords_by_traffic = sorted(keywords, key=lambda x: x.get('etv', 0), reverse=True)
            
            # Quick wins (keywords ranking 11-20 with good traffic potential)
            quick_wins = [
                kw for kw in position_ranges["positions_11_20"]
                if kw.get('search_volume', 0) > 100
            ]
            quick_wins.sort(key=lambda x: x.get('search_volume', 0), reverse=True)
            
            # Prepare response
            result = {
                "domain": domain,
                "total_keywords": len(keywords),
                "total_traffic": round(total_traffic, 2),
                "total_search_volume": total_search_volume,
                "avg_position": round(avg_position, 1),
                "keywords": keywords,
                "overview": {
                    "top_3_count": len(position_ranges["top_3"]),
                    "top_10_count": len(position_ranges["top_3"]) + len(position_ranges["top_10"]),
                    "positions_11_20": len(position_ranges["positions_11_20"]),
                    "positions_21_50": len(position_ranges["positions_21_50"]),
                    "positions_50_plus": len(position_ranges["positions_50_plus"])
                },
                "top_traffic_keywords": keywords_by_traffic[:10],
                "quick_wins": quick_wins[:10],
                "position_distribution": position_ranges,
                "insights": self._generate_domain_insights(
                    keywords, total_traffic, avg_position, position_ranges
                )
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Domain analysis error: {str(e)}")
            raise
    
    def _generate_domain_insights(
        self, 
        keywords: List[Dict],
        total_traffic: float,
        avg_position: float,
        position_ranges: Dict
    ) -> Dict[str, Any]:
        """Generate AI-powered insights for domain analysis"""
        try:
            # Basic insights without AI (in case LLM fails)
            insights = {
                "summary": f"Domain ranks for {len(keywords)} keywords with estimated traffic of {total_traffic:.0f} visits/month",
                "strengths": [],
                "opportunities": [],
                "recommendations": []
            }
            
            # Identify strengths
            if len(position_ranges["top_3"]) > 5:
                insights["strengths"].append(f"Strong presence with {len(position_ranges['top_3'])} keywords in top 3 positions")
            
            if total_traffic > 1000:
                insights["strengths"].append(f"Healthy traffic flow with {total_traffic:.0f} estimated monthly visits")
            
            # Identify opportunities
            quick_win_count = len(position_ranges["positions_11_20"])
            if quick_win_count > 0:
                insights["opportunities"].append(f"{quick_win_count} keywords ranking 11-20 can be pushed to page 1")
            
            if avg_position > 20:
                insights["opportunities"].append("Average position is low - focus on optimization")
            
            # Recommendations
            if len(position_ranges["top_3"]) < 3:
                insights["recommendations"].append("Focus on moving top 10 keywords to top 3 positions")
            
            if quick_win_count > 5:
                insights["recommendations"].append("Prioritize content optimization for position 11-20 keywords")
            
            # Try to get AI insights
            if self.llm_client:
                try:
                    prompt = f"""Analyze this domain's SEO performance:
                    - Total Keywords: {len(keywords)}
                    - Estimated Traffic: {total_traffic:.0f} visits/month
                    - Average Position: {avg_position:.1f}
                    - Top 3 positions: {len(position_ranges['top_3'])} keywords
                    - Positions 11-20: {len(position_ranges['positions_11_20'])} keywords
                    
                    Provide 3 concise, actionable recommendations to improve traffic. Keep each recommendation under 100 words."""
                    
                    ai_insights = self.llm_client.generate_text(prompt, max_tokens=1000, temperature=0.3)
                    insights["ai_recommendations"] = ai_insights
                except:
                    pass  # Fallback to basic insights
            
            return insights
            
        except Exception as e:
            print(f"Error generating insights: {e}")
            return {"summary": "Analysis complete", "recommendations": []}
