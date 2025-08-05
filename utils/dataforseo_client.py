"""
DataForSEO REST API Client
Direct API integration for Streamlit Cloud compatibility
"""

import os
import requests
import base64
from typing import List, Dict, Any, Optional


class DataForSEOClient:
    """Direct DataForSEO REST API client"""
    
    def __init__(self):
        self.username = os.getenv("DATAFORSEO_USERNAME")
        self.password = os.getenv("DATAFORSEO_PASSWORD")
        
        if not self.username or not self.password:
            print("⚠️ DataForSEO credentials not found. Using mock data mode.")
            self.use_fallback = True
        else:
            self.use_fallback = False
            
        # Create auth header
        credentials = f"{self.username}:{self.password}"
        self.auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        # API endpoints
        self.base_url = "https://api.dataforseo.com/v3"
        
        # API status
        self._check_connection()
    
    def _check_connection(self):
        """Check if we can connect to DataForSEO API"""
        if self.use_fallback:
            return
            
        try:
            # Use a simple endpoint to check connection
            response = requests.get(
                f"{self.base_url}/appendix/user_data",
                headers={"Authorization": self.auth_header},
                timeout=5
            )
            if response.status_code == 200:
                print("✅ DataForSEO API connected successfully")
            else:
                print(f"⚠️ DataForSEO API returned status {response.status_code}")
                self.use_fallback = True
        except Exception as e:
            print(f"❌ Failed to connect to DataForSEO: {str(e)}")
            self.use_fallback = True
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Make API request with error handling"""
        if self.use_fallback:
            return None
            
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                json=[data],  # DataForSEO expects array of tasks
                headers={"Authorization": self.auth_header},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status_code") == 20000:
                    tasks = result.get("tasks", [])
                    if tasks and tasks[0].get("status_code") == 20000:
                        return tasks[0]
                    else:
                        print(f"Task error: {tasks[0].get('status_message') if tasks else 'No tasks returned'}")
                else:
                    print(f"API error: {result.get('status_message', 'Unknown error')}")
            else:
                print(f"HTTP error {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"Request failed: {str(e)}")
            
        return None
    
    def get_keyword_suggestions(
        self,
        seed_keyword: str,
        location: str = "United States",
        language: str = "English",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get keyword suggestions via REST API"""
        
        # Preprocess keyword
        processed_keyword = seed_keyword.strip()
        if len(processed_keyword.split()) > 4:
            processed_keyword = ' '.join(processed_keyword.split()[:4])
            print(f"🔑 Simplified keyword: '{seed_keyword}' → '{processed_keyword}'")
        
        data = {
            "keywords": [processed_keyword],
            "location_name": location,
            "language_name": language,
            "limit": limit,
            "include_seed_keyword": True,
            "include_serp_info": False
        }
        
        result = self._make_request("dataforseo_labs/google/keyword_ideas/live", data)
        
        if result and result.get("result"):
            items = result["result"][0].get("items", [])
            processed_items = []
            
            for item in items:
                if item.get("keyword_info"):
                    processed_items.append({
                        "keyword": item.get("keyword", ""),
                        "search_volume": item["keyword_info"].get("search_volume", 0),
                        "competition": item["keyword_info"].get("competition", 0),
                        "cpc": item["keyword_info"].get("cpc", 0),
                        "difficulty": int((item["keyword_info"].get("competition") or 0) * 100)
                    })
            
            return processed_items
        
        return []
    
    def get_serp_analysis(
        self,
        keyword: str,
        location: str = "United States",
        language: str = "English"
    ) -> List[Dict[str, Any]]:
        """Get SERP analysis via REST API"""
        
        # Preprocess keyword
        processed_keyword = keyword.strip()
        if len(processed_keyword.split()) > 4:
            processed_keyword = ' '.join(processed_keyword.split()[:4])
            print(f"🔍 Simplified SERP query: '{keyword}' → '{processed_keyword}'")
        
        data = {
            "keyword": processed_keyword,
            "location_name": location,
            "language_name": language,
            "depth": 10
        }
        
        result = self._make_request("serp/google/organic/live/regular", data)
        
        if result and result.get("result"):
            items = result["result"][0].get("items", [])
            processed_items = []
            
            for item in items:
                if item.get("type") == "organic":
                    processed_items.append({
                        "position": item.get("rank_group", 0),
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "domain": item.get("domain", "")
                    })
            
            return processed_items[:10]
        
        return []
    
    def get_search_volume_data(
        self,
        keywords: List[str],
        location: str = "United States",
        language: str = "English"
    ) -> List[Dict[str, Any]]:
        """Get search volume data via REST API"""
        
        # Preprocess keywords
        processed_keywords = []
        for kw in keywords:
            kw = kw.strip()
            if len(kw.split()) > 4:
                kw = ' '.join(kw.split()[:4])
            processed_keywords.append(kw)
        
        data = {
            "keywords": processed_keywords,
            "location_name": location,
            "language_name": language,
            "sort_by": "search_volume"
        }
        
        result = self._make_request("keywords_data/google_ads/search_volume/live", data)
        
        if result and result.get("result"):
            items = result["result"]
            processed_items = []
            
            for item in items:
                # Process monthly searches to avoid [object Object] display
                monthly_data = item.get("monthly_searches", [])
                monthly_summary = ""
                if monthly_data:
                    # Get last 3 months for summary
                    recent_months = monthly_data[:3]
                    monthly_summary = ", ".join([
                        f"{m['year']}-{m['month']:02d}: {m['search_volume']:,}"
                        for m in recent_months
                    ])
                
                processed_items.append({
                    "keyword": item.get("keyword", ""),
                    "search_volume": item.get("search_volume", 0),
                    "competition": item.get("competition", 0),
                    "cpc": item.get("cpc", 0),
                    "monthly_searches": monthly_summary or "No data",
                    "monthly_data_raw": monthly_data  # Keep raw data for charts
                })
            
            return processed_items
        
        return []
    
    def get_competitor_domains(
        self,
        target_domain: str,
        location: str = "United States",
        language: str = "English"
    ) -> List[Dict[str, Any]]:
        """Get competitor domains via REST API"""
        
        # Clean domain
        from urllib.parse import urlparse
        parsed = urlparse(target_domain if target_domain.startswith('http') else f'https://{target_domain}')
        clean_domain = parsed.netloc or parsed.path
        clean_domain = clean_domain.replace('www.', '')
        
        data = {
            "target": clean_domain,
            "location_name": location,
            "language_name": language,
            "item_types": ["organic"],
            "limit": 10
        }
        
        result = self._make_request("dataforseo_labs/google/competitors_domain/live", data)
        
        if result and result.get("result"):
            items = result["result"][0].get("items", [])
            processed_items = []
            
            # Skip first item (it's usually the target domain itself)
            for item in items[1:]:
                if item.get("domain"):
                    processed_items.append({
                        "domain": item.get("domain", ""),
                        "avg_position": item.get("avg_position", 0),
                        "sum_position": item.get("sum_position", 0),
                        "intersections": item.get("intersections", 0),
                        "relevant_serp_items": item.get("relevant_serp_items", 0),
                        "etv": item.get("metrics", {}).get("organic", {}).get("etv", 0)
                    })
            
            return processed_items
        
        return []
    
    def get_ranked_keywords(
        self,
        target_domain: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get keywords a domain ranks for via REST API"""
        
        # Clean domain
        from urllib.parse import urlparse
        parsed = urlparse(target_domain if target_domain.startswith('http') else f'https://{target_domain}')
        clean_domain = parsed.netloc or parsed.path
        clean_domain = clean_domain.replace('www.', '')
        
        data = {
            "target": clean_domain,
            "location_code": 2840,  # United States
            "language_code": "en",
            "limit": limit,
            "order_by": ["keyword_data.keyword_info.search_volume,desc"]
        }
        
        result = self._make_request("dataforseo_labs/google/ranked_keywords/live", data)
        
        if result and result.get("result"):
            items = result["result"][0].get("items", [])
            processed_items = []
            
            for item in items:
                if item.get("keyword_data"):
                    kw_info = item["keyword_data"].get("keyword_info", {})
                    processed_items.append({
                        "keyword": item["keyword_data"].get("keyword", ""),
                        "position": item.get("ranked_serp_element", {}).get("serp_item", {}).get("rank_group", 0),
                        "search_volume": kw_info.get("search_volume", 0),
                        "url": item.get("ranked_serp_element", {}).get("serp_item", {}).get("url", ""),
                        "etv": item.get("ranked_serp_element", {}).get("serp_item", {}).get("etv", 0)
                    })
            
            return processed_items
        
        return []
    
    def get_trends_data(
        self,
        keywords: List[str],
        time_range: str = "past_12_months"
    ) -> Dict[str, Any]:
        """Get Google Trends data via REST API"""
        
        # Preprocess keywords
        processed_keywords = []
        for kw in keywords[:5]:  # Google Trends allows max 5 keywords
            kw = kw.strip()
            if len(kw.split()) > 4:
                kw = ' '.join(kw.split()[:4])
            processed_keywords.append(kw)
        
        data = {
            "keywords": processed_keywords,
            "location_name": "United States",
            "language_name": "English",
            "time_range": time_range
        }
        
        result = self._make_request("keywords_data/google_trends/explore/live", data)
        
        if result and result.get("result"):
            items = result["result"][0].get("items", [])
            
            if items and items[0].get("data"):
                trends_data = items[0]["data"]
                
                # Process interest over time
                interest_data = []
                for point in trends_data.get("interest_over_time", {}).get("timeline_data", []):
                    if not point.get("values", [{}])[0].get("missing_data", False):
                        interest_data.append({
                            "date": point.get("date_from", ""),
                            "values": {processed_keywords[i]: v.get("value", 0) 
                                     for i, v in enumerate(point.get("values", []))}
                        })
                
                return {
                    "keywords": processed_keywords,
                    "interest_over_time": interest_data,
                    "related_queries": trends_data.get("related_queries", {})
                }
        
        return {"keywords": processed_keywords, "interest_over_time": [], "related_queries": {}}
    
    def analyze_content(
        self,
        url: str
    ) -> Dict[str, Any]:
        """Analyze on-page content via REST API"""
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        data = {
            "url": url,
            "enable_javascript": True,
            "load_resources": True,
            "enable_browser_rendering": True
        }
        
        result = self._make_request("on_page/instant_pages", data)
        
        if result and result.get("result"):
            items = result["result"][0].get("items", [])
            
            if items:
                page_data = items[0]
                onpage_result = page_data.get("onpage_result", {})
                
                return {
                    "url": url,
                    "status_code": page_data.get("status_code", 0),
                    "onpage_score": onpage_result.get("onpage_score", 0),
                    "meta": onpage_result.get("meta", {}),
                    "page_timing": onpage_result.get("page_timing", {}),
                    "checks": onpage_result.get("checks", {}),
                    "content_metrics": {
                        "word_count": onpage_result.get("word_count", 0),
                        "images_count": onpage_result.get("images_count", 0),
                        "links_count": onpage_result.get("internal_links_count", 0) + 
                                      onpage_result.get("external_links_count", 0),
                        "readability": onpage_result.get("flesch_kincaid_readability", 0)
                    }
                }
        
        return {}