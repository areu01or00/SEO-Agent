"""
Enhanced data processing methods for DataForSEO MCP responses
"""
import json
from typing import Dict, List, Any
import random

def process_ranked_keywords_data(raw_data: Dict) -> List[Dict[str, Any]]:
    """Process ranked keywords data from MCP response"""
    keywords = []
    
    try:
        if "content" in raw_data and raw_data["content"]:
            content_text = raw_data["content"][0].get("text", "{}")
            parsed_data = json.loads(content_text)
            items = parsed_data.get("items", [])
        else:
            items = []
        
        for item in items:
            keyword_data = item.get("keyword_data", {})
            keyword_info = keyword_data.get("keyword_info", {})
            serp_item = item.get("ranked_serp_element", {}).get("serp_item", {})
            
            result = {
                "keyword": keyword_data.get("keyword", ""),
                "search_volume": keyword_info.get("search_volume", 0),
                "difficulty": keyword_info.get("keyword_difficulty", 0),
                "cpc": keyword_info.get("cpc", 0.0),
                "competition": keyword_info.get("competition", 0.0),
                "position": serp_item.get("rank_absolute", 0),
                "url": serp_item.get("url", ""),
                "title": serp_item.get("title", ""),
                "type": "Ranked"
            }
            keywords.append(result)
        
        return keywords
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error processing ranked keywords data: {e}")
        return []

def process_competitor_data(raw_data: Dict) -> List[Dict[str, Any]]:
    """Process competitor domains data from MCP response"""
    competitors = []
    
    try:
        if "content" in raw_data and raw_data["content"]:
            content_text = raw_data["content"][0].get("text", "{}")
            parsed_data = json.loads(content_text)
            items = parsed_data.get("items", [])
        else:
            items = []
        
        # Skip the first item (it's the target domain, not a competitor)
        for item in items[1:]:  # Start from index 1
            metrics = item.get("metrics", {})
            organic = metrics.get("organic", {})
            
            competitor = {
                "domain": item.get("domain", ""),
                "common_keywords": item.get("intersections", 0),  # Use intersections for common keywords
                "se_keywords": organic.get("count", 0),
                "estimated_traffic": organic.get("etv", 0),
                "avg_position": item.get("avg_position", 0),  # avg_position is at item level
                "visibility": organic.get("visibility", 0.0),
                "relevance": round(item.get("intersections", 0) / max(organic.get("count", 1), 1), 3)  # Calculate relevance
            }
            competitors.append(competitor)
        
        return competitors
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error processing competitor data: {e}")
        return []

def process_search_volume_data(raw_data: Dict) -> List[Dict[str, Any]]:
    """Process search volume data from MCP response"""
    results = []
    
    try:
        if "content" in raw_data and raw_data["content"]:
            content_text = raw_data["content"][0].get("text", "{}")
            parsed_data = json.loads(content_text)
            items = parsed_data.get("items", [])
        else:
            items = []
        
        for item in items:
            # DataForSEO ads search volume response structure
            monthly_searches = item.get("monthly_searches", [])
            
            result = {
                "keyword": item.get("keyword", ""),
                "search_volume": item.get("search_volume", 0),
                "cpc": item.get("cpc", 0.0),
                "competition": item.get("competition", 0.0),
                "competition_level": item.get("competition_index", "UNKNOWN"),
                "monthly_searches": monthly_searches,
                "low_bid": item.get("low_top_of_page_bid", 0.0),
                "high_bid": item.get("high_top_of_page_bid", 0.0)
            }
            results.append(result)
        
        return results
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error processing search volume data: {e}")
        return []

def process_trends_data(raw_data: Dict) -> Dict[str, Any]:
    """Process Google Trends data from MCP response"""
    
    try:
        if "content" in raw_data and raw_data["content"]:
            content_text = raw_data["content"][0].get("text", "{}")
            parsed_data = json.loads(content_text)
            items = parsed_data.get("items", [])
        else:
            items = []
        
        trends_data = {
            "keywords": [],
            "graph_data": [],
            "related_queries": [],
            "rising_queries": []
        }
        
        for item in items:
            if item.get("type") == "google_trends_graph":
                # Extract keywords and graph data
                trends_data["keywords"] = item.get("keywords", [])
                raw_data_points = item.get("data", [])
                
                # Convert to the expected format with date and value
                graph_data = []
                for point in raw_data_points:
                    if isinstance(point, dict):
                        # Skip points with missing data
                        if point.get("missing_data", False):
                            continue
                            
                        # Extract date and value from DataForSEO format
                        date = point.get("date_from", "")
                        values = point.get("values", [])
                        value = values[0] if values and len(values) > 0 else 0
                        
                        if date:
                            graph_data.append({
                                "date": date,
                                "value": value
                            })
                
                trends_data["graph_data"] = graph_data
                
            elif item.get("type") == "google_trends_queries_list":
                queries = item.get("queries", [])
                trends_data["related_queries"] = [q.get("query", "") for q in queries[:10]]
                trends_data["rising_queries"] = [q.get("query", "") for q in queries[10:20]]
        
        return trends_data
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error processing trends data: {e}")
        return {"keywords": [], "graph_data": [], "related_queries": [], "rising_queries": []}

def process_content_analysis_data(raw_data: Dict) -> Dict[str, Any]:
    """Process content analysis data from MCP response"""
    
    try:
        if "content" in raw_data and raw_data["content"]:
            content_text = raw_data["content"][0].get("text", "{}")
            
            # Check for API errors first
            if content_text.startswith("Error:"):
                print(f"API Error from DataForSEO: {content_text}")
                return {}
            
            # Debug: Check if content_text is empty or invalid
            if not content_text or content_text.strip() == "":
                print(f"Warning: Empty content text from MCP response")
                return {}
            
            # Try to parse JSON with better error handling
            try:
                parsed_data = json.loads(content_text)
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error: {json_err}")
                print(f"Content text (first 200 chars): {content_text[:200]}")
                return {}
            
            # Check for API error in parsed data
            if parsed_data.get("status_code") != 20000:
                print(f"DataForSEO API error: {parsed_data.get('status_message', 'Unknown error')}")
                return {}
                
            items = parsed_data.get("items", [])
        else:
            print("Warning: No content found in MCP response")
            items = []
        
        if items:
            item = items[0]
            meta = item.get("meta", {})
            htags = meta.get("htags", {})
            content = meta.get("content", {})
            checks = item.get("checks", {})
            page_timing = item.get("page_timing", {})
            
            analysis = {
                "url": item.get("url", ""),
                "title": meta.get("title", ""),
                "meta_description": meta.get("description", "N/A"),
                "h1_tags": htags.get("h1", []),
                "h2_tags": htags.get("h2", []),
                "h3_tags": htags.get("h3", []),
                "word_count": content.get("plain_text_word_count", 0),
                "internal_links": meta.get("internal_links_count", 0),
                "external_links": meta.get("external_links_count", 0),
                "images": meta.get("images_count", 0),
                "text_content": content.get("plain_text_size", 0),
                "onpage_score": item.get("onpage_score", 0),
                "page_size": item.get("size", 0),
                "load_time": page_timing.get("duration_time", 0),
                "seo_checks": {
                    "has_https": checks.get("is_https", False),
                    "has_title": not checks.get("title_too_short", True),
                    "has_description": not checks.get("no_description", True),
                    "has_favicon": not checks.get("no_favicon", True),
                    "seo_friendly_url": checks.get("seo_friendly_url", False),
                    "has_h1_tag": not checks.get("no_h1_tag", True),
                    "has_canonical": checks.get("canonical", False)
                },
                "readability": {
                    "flesch_kincaid": content.get("flesch_kincaid_readability_index", 0),
                    "automated_readability": content.get("automated_readability_index", 0),
                    "coleman_liau": content.get("coleman_liau_readability_index", 0),
                    "dale_chall": content.get("dale_chall_readability_index", 0),
                    "smog": content.get("smog_readability_index", 0)
                },
                "performance": {
                    "time_to_interactive": page_timing.get("time_to_interactive", 0),
                    "dom_complete": page_timing.get("dom_complete", 0),
                    "connection_time": page_timing.get("connection_time", 0),
                    "download_time": page_timing.get("download_time", 0)
                }
            }
            
            return analysis
        
        return {}
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error processing content analysis data: {e}")
        return {}

# Mock data generators for fallback
def generate_mock_ranked_keywords(domain: str, limit: int) -> List[Dict[str, Any]]:
    """Generate mock ranked keywords data"""
    keywords = []
    base_keywords = ["marketing", "seo", "digital", "content", "strategy", "tools", "analytics", "optimization"]
    
    for i in range(min(limit, 20)):
        keyword = f"{random.choice(base_keywords)} {random.choice(['tips', 'guide', 'tools', 'strategy'])}"
        keywords.append({
            "keyword": keyword,
            "search_volume": random.randint(100, 10000),
            "difficulty": random.randint(20, 80),
            "cpc": round(random.uniform(0.5, 5.0), 2),
            "competition": round(random.uniform(0.1, 0.9), 2),
            "position": random.randint(1, 10),
            "url": f"https://{domain}/page{i+1}",
            "title": f"{keyword.title()} - {domain.title()}",
            "type": "Ranked"
        })
    
    return keywords

def generate_mock_competitor_data(domain: str, limit: int) -> List[Dict[str, Any]]:
    """Generate mock competitor data"""
    competitors = []
    competitor_domains = ["competitor1.com", "competitor2.com", "rival-site.com", "industry-leader.com", "market-leader.com"]
    
    for i in range(min(limit, len(competitor_domains))):
        competitors.append({
            "domain": competitor_domains[i],
            "common_keywords": random.randint(50, 500),
            "se_keywords": random.randint(1000, 10000),
            "estimated_traffic": random.randint(5000, 50000),
            "avg_position": round(random.uniform(5, 25), 1),
            "visibility": round(random.uniform(0.1, 0.8), 3),
            "relevance": round(random.uniform(0.5, 1.0), 2)
        })
    
    return competitors

def generate_mock_search_volume_data(keywords: List[str]) -> List[Dict[str, Any]]:
    """Generate mock search volume data"""
    results = []
    
    for keyword in keywords:
        results.append({
            "keyword": keyword,
            "search_volume": random.randint(100, 50000),
            "cpc": round(random.uniform(0.3, 8.0), 2),
            "competition": round(random.uniform(0.1, 0.9), 2),
            "competition_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
            "monthly_searches": {
                f"2024-{i:02d}": random.randint(80, 120) * (random.randint(100, 50000) // 100)
                for i in range(1, 13)
            },
            "categories": [random.randint(10000, 15000) for _ in range(3)]
        })
    
    return results

def generate_mock_trends_data(keywords: List[str]) -> Dict[str, Any]:
    """Generate mock trends data"""
    return {
        "keywords": keywords,
        "graph_data": [
            {"date": f"2024-{i:02d}-01", "value": random.randint(40, 100)}
            for i in range(1, 13)
        ],
        "related_queries": [
            f"{keywords[0] if keywords else 'keyword'} {suffix}"
            for suffix in ["guide", "tutorial", "tips", "best practices", "tools"]
        ],
        "rising_queries": [
            f"new {keywords[0] if keywords else 'keyword'} {suffix}"
            for suffix in ["trends", "techniques", "strategies", "methods", "approaches"]
        ]
    }

def generate_mock_content_analysis(url: str) -> Dict[str, Any]:
    """Generate mock content analysis data"""
    return {
        "url": url,
        "title": f"Sample Page Title - {url.split('/')[-1] if '/' in url else url}",
        "meta_description": "This is a sample meta description for the analyzed page.",
        "h1_tags": ["Main Heading", "Secondary Heading"],
        "h2_tags": ["Section 1", "Section 2", "Section 3"],
        "h3_tags": ["Subsection 1.1", "Subsection 1.2", "Subsection 2.1"],
        "word_count": random.randint(500, 3000),
        "internal_links": random.randint(10, 50),
        "external_links": random.randint(5, 20),
        "images": random.randint(3, 15),
        "text_content": random.randint(400, 2500)
    }