import json
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional
from .enhanced_processing import (
    process_ranked_keywords_data, process_competitor_data, 
    process_search_volume_data, process_trends_data, process_content_analysis_data,
    generate_mock_ranked_keywords, generate_mock_competitor_data,
    generate_mock_search_volume_data, generate_mock_trends_data, generate_mock_content_analysis
)

class MCPClient:
    """
    Client for interacting with MCP servers
    """
    
    def __init__(self):
        self.servers = {}
        self.active_connections = {}
    
    def configure_dataforseo_server(self):
        """Configure DataForSEO MCP server"""
        try:
            # Check if running on Streamlit Cloud
            if os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud":
                # Try to install MCP server if not already installed
                try:
                    subprocess.run(["which", "dataforseo-mcp-server"], check=True, capture_output=True)
                    print("✅ DataForSEO MCP server already installed")
                except subprocess.CalledProcessError:
                    print("📦 Installing DataForSEO MCP server...")
                    try:
                        # Install globally without sudo (Streamlit Cloud allows this)
                        result = subprocess.run(
                            ["npm", "install", "-g", "dataforseo-mcp-server"],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        if result.returncode == 0:
                            print("✅ DataForSEO MCP server installed successfully")
                        else:
                            print(f"❌ Failed to install MCP server: {result.stderr}")
                            self.use_fallback = True
                            return False
                    except Exception as install_error:
                        print(f"❌ Installation error: {install_error}")
                        self.use_fallback = True
                        return False
            
            # Official DataForSEO MCP server configuration
            self.servers["dataforseo"] = {
                "command": "dataforseo-mcp-server",
                "args": [],
                "env": {
                    "DATAFORSEO_USERNAME": os.getenv("DATAFORSEO_USERNAME"),
                    "DATAFORSEO_PASSWORD": os.getenv("DATAFORSEO_PASSWORD")
                }
            }
            
            print("✅ Official DataForSEO MCP server configured")
            return True
            
        except Exception as e:
            print(f"❌ Failed to configure DataForSEO MCP server: {str(e)}")
            self.use_fallback = True
            return False
    
    def call_tool(self, server_name: str, tool_name: str, arguments: Dict = None) -> Dict:
        """
        Call a tool on an MCP server using proper stdio communication
        """
        try:
            if server_name not in self.servers:
                raise Exception(f"Server {server_name} not configured")
            
            server_config = self.servers[server_name]
            
            # Prepare MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments or {}
                }
            }
            
            # Execute MCP server command with proper stdio
            env = os.environ.copy()
            env.update(server_config.get("env", {}))
            
            cmd = server_config["command"]
            args = server_config["args"]
            
            # Start the MCP server process
            try:
                process = subprocess.Popen(
                    [cmd] + args,
                    env=env,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            except FileNotFoundError:
                print(f"❌ MCP server command '{cmd}' not found. Using fallback mode.")
                return {"error": f"MCP server '{cmd}' not installed"}
            
            # Send request and get response
            request_json = json.dumps(request) + '\n'
            stdout, stderr = process.communicate(input=request_json, timeout=30)
            
            if process.returncode != 0:
                raise Exception(f"MCP server error: {stderr}")
            
            # Parse response - get the last line that looks like JSON
            lines = stdout.strip().split('\n')
            response_line = None
            
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('{"') and '"jsonrpc"' in line:
                    response_line = line
                    break
            
            if not response_line:
                raise Exception(f"No valid JSON response found in: {stdout}")
            
            response = json.loads(response_line)
            
            if "error" in response:
                raise Exception(f"Tool error: {response['error']}")
            
            return response.get("result", {})
                    
        except Exception as e:
            print(f"MCP tool call failed: {str(e)}")
            return {"error": str(e)}
    
    def list_tools(self, server_name: str) -> List[Dict]:
        """List available tools on an MCP server"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            # This is a simplified version - in practice, you'd establish a proper MCP connection
            # For now, return expected DataForSEO tools
            if server_name == "dataforseo":
                return [
                    {
                        "name": "dataforseo_keywords_data",
                        "description": "Get keyword suggestions and search volume data"
                    },
                    {
                        "name": "dataforseo_serp_analysis", 
                        "description": "Analyze SERP results for keywords"
                    },
                    {
                        "name": "dataforseo_keyword_difficulty",
                        "description": "Get keyword difficulty scores"
                    }
                ]
            
            return []
            
        except Exception as e:
            print(f"Failed to list tools: {str(e)}")
            return []

class DataForSEOMCP:
    """
    Enhanced DataForSEO MCP integration with full API capabilities
    Supports SERP, Keywords Data, On-Page, DataForSEO Labs, Business Data, 
    Domain Analytics, and Backlinks modules
    """
    
    def __init__(self):
        self.client = MCPClient()
        
        # Try to use real MCP server first, fallback to mock if unavailable
        self.use_fallback = False
        
        # Configure server and check if we need fallback
        if not self.client.configure_dataforseo_server():
            print("⚠️ Using mock data fallback mode")
            self.use_fallback = True
        
        # Available API modules based on research
        self.available_modules = {
            "SERP": ["serp_organic_live_advanced", "serp_youtube_organic_live_advanced"],
            "KEYWORDS_DATA": ["keywords_data_google_ads_search_volume", "keywords_data_google_trends_explore"],
            "DATAFORSEO_LABS": ["dataforseo_labs_google_keyword_ideas", "dataforseo_labs_google_ranked_keywords", "dataforseo_labs_google_competitors_domain"],
            "ON_PAGE": ["on_page_content_parsing", "on_page_instant_pages"],
            "BUSINESS_DATA": [],
            "DOMAIN_ANALYTICS": [],
            "BACKLINKS": []
        }
    
    def get_keyword_suggestions(
        self,
        seed_keyword: str,
        location: str = "United States",
        language: str = "English",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get keyword suggestions via MCP"""
        
        try:
            # Preprocess seed keyword for better results  
            processed_keyword = self._preprocess_keywords([seed_keyword])[0]
            if len(seed_keyword.split()) > 4:
                processed_keyword = self._simplify_keywords([seed_keyword])[0]
                print(f"🔑 Simplified keyword query: '{seed_keyword}' → '{processed_keyword}'")
            
            # Try MCP first
            if not self.use_fallback:
                result = self.client.call_tool(
                    "dataforseo",
                    "dataforseo_labs_google_keyword_ideas",
                    {
                        "keywords": [processed_keyword],
                        "location_name": location,
                        "language_code": language.lower()[:2],
                        "limit": limit
                    }
                )
                
                if not result.get("error"):
                    return self._process_keyword_data(result)
            
            # Fallback to mock data for development
            return self._generate_mock_keyword_data(seed_keyword, limit)
            
        except Exception as e:
            print(f"MCP keyword suggestions failed: {str(e)}")
            return self._generate_mock_keyword_data(seed_keyword, limit)
    
    def get_serp_analysis(
        self,
        keyword: str,
        location: str = "United States",
        language: str = "English"
    ) -> List[Dict[str, Any]]:
        """Get SERP analysis via MCP"""
        
        try:
            # Preprocess keyword for better results
            processed_keyword = self._preprocess_keywords([keyword])[0]
            if len(keyword.split()) > 4:
                processed_keyword = self._simplify_keywords([keyword])[0]
                print(f"🔍 Simplified SERP query: '{keyword}' → '{processed_keyword}'")
            
            # Try MCP first
            if not self.use_fallback:
                result = self.client.call_tool(
                    "dataforseo",
                    "serp_organic_live_advanced",
                    {
                        "keyword": processed_keyword,
                        "location_name": location,
                        "language_code": language.lower()[:2],
                        "depth": 10
                    }
                )
                
                if not result.get("error"):
                    return self._process_serp_data(result)
            
            # Fallback to mock data
            return self._generate_mock_serp_data(keyword)
            
        except Exception as e:
            print(f"MCP SERP analysis failed: {str(e)}")
            return self._generate_mock_serp_data(keyword)
    
    def get_ranked_keywords(
        self,
        target_domain: str,
        location: str = "United States",
        language: str = "English",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get keywords that a domain is ranking for"""
        
        try:
            if not self.use_fallback:
                result = self.client.call_tool(
                    "dataforseo",
                    "dataforseo_labs_google_ranked_keywords",
                    {
                        "target": target_domain,
                        "location_name": location,
                        "language_code": language.lower()[:2],
                        "limit": limit
                    }
                )
                
                if not result.get("error"):
                    return process_ranked_keywords_data(result)
            
            return generate_mock_ranked_keywords(target_domain, limit)
            
        except Exception as e:
            print(f"MCP ranked keywords failed: {str(e)}")
            return generate_mock_ranked_keywords(target_domain, limit)
    
    def get_competitor_domains(
        self,
        target_domain: str,
        location: str = "United States", 
        language: str = "English",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get competitor domains for a target domain"""
        
        try:
            if not self.use_fallback:
                result = self.client.call_tool(
                    "dataforseo",
                    "dataforseo_labs_google_competitors_domain",
                    {
                        "target": target_domain,
                        "location_name": location,
                        "language_code": language.lower()[:2],
                        "limit": limit
                    }
                )
                
                if not result.get("error"):
                    return process_competitor_data(result)
            
            return generate_mock_competitor_data(target_domain, limit)
            
        except Exception as e:
            print(f"MCP competitor analysis failed: {str(e)}")
            return generate_mock_competitor_data(target_domain, limit)
    
    def _preprocess_keywords(self, keywords: List[str]) -> List[str]:
        """Preprocess keywords for better API results"""
        processed = []
        for kw in keywords:
            # Truncate very long keywords
            if len(kw) > 80:
                kw = kw[:80]
            # Remove special characters that might cause issues
            kw = kw.replace('"', '').replace("'", '')
            processed.append(kw)
        return processed
    
    def _simplify_keywords(self, keywords: List[str]) -> List[str]:
        """Simplify complex keywords to get better data"""
        simplified = []
        for kw in keywords:
            # For very specific queries, extract core terms
            if len(kw.split()) > 5:
                # Take first 3-4 words for better results
                words = kw.split()[:4]
                simplified.append(' '.join(words))
            else:
                simplified.append(kw)
        return simplified
    
    def get_search_volume_data(
        self,
        keywords: List[str],
        location: str = "United States",
        language: str = "English"
    ) -> List[Dict[str, Any]]:
        """Get search volume data for specific keywords"""
        
        try:
            # Preprocess long/complex keywords
            processed_keywords = self._preprocess_keywords(keywords)
            
            if not self.use_fallback:
                result = self.client.call_tool(
                    "dataforseo",
                    "keywords_data_google_ads_search_volume",
                    {
                        "keywords": processed_keywords,
                        "location_name": location,
                        "language_code": language.lower()[:2]
                    }
                )
                
                if not result.get("error"):
                    volume_data = process_search_volume_data(result)
                    # Add warning for zero-volume keywords
                    for i, vd in enumerate(volume_data):
                        if vd.get('search_volume', 0) == 0 and len(keywords[i]) > 30:
                            vd['note'] = 'Query too specific - try shorter keywords'
                    return volume_data
            
            return generate_mock_search_volume_data(keywords)
            
        except Exception as e:
            print(f"MCP search volume failed: {str(e)}")
            return generate_mock_search_volume_data(keywords)
    
    def get_trends_data(
        self,
        keywords: List[str],
        location: str = "United States",
        time_range: str = "past_12_months"
    ) -> Dict[str, Any]:
        """Get Google Trends data for keywords"""
        
        try:
            # Preprocess and simplify keywords for trends
            processed_keywords = self._preprocess_keywords(keywords)
            # For trends, simplify complex queries more aggressively
            if any(len(kw.split()) > 4 for kw in processed_keywords):
                processed_keywords = self._simplify_keywords(processed_keywords)
                print(f"📈 Simplified query for trends: {processed_keywords}")
            
            if not self.use_fallback:
                result = self.client.call_tool(
                    "dataforseo",
                    "keywords_data_google_trends_explore",
                    {
                        "keywords": processed_keywords,
                        "location_name": location,
                        "time_range": time_range,
                        "type": "web"
                    }
                )
                
                if not result.get("error"):
                    trends_data = process_trends_data(result)
                    # Add note if keyword was simplified
                    if processed_keywords != keywords:
                        trends_data['note'] = f'Showing trends for simplified query: {", ".join(processed_keywords)}'
                    return trends_data
            
            return generate_mock_trends_data(keywords)
            
        except Exception as e:
            print(f"MCP trends analysis failed: {str(e)}")
            return generate_mock_trends_data(keywords)
    
    def get_content_analysis(
        self,
        url: str,
        enable_javascript: bool = True
    ) -> Dict[str, Any]:
        """Analyze on-page content of a URL"""
        
        try:
            if not self.use_fallback:
                # Ensure URL has proper protocol
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                result = self.client.call_tool(
                    "dataforseo",
                    "on_page_instant_pages",
                    {
                        "url": url,
                        "enable_javascript": enable_javascript
                    }
                )
                
                if not result.get("error"):
                    processed_result = process_content_analysis_data(result)
                    # If processing returns empty dict, use fallback
                    if processed_result:
                        return processed_result
                    else:
                        print(f"MCP returned empty content analysis for {url}, using fallback")
            
            return generate_mock_content_analysis(url)
            
        except Exception as e:
            print(f"MCP content analysis failed: {str(e)}")
            return generate_mock_content_analysis(url)
    
    def _process_keyword_data(self, raw_data: Dict) -> List[Dict[str, Any]]:
        """Process raw keyword data from MCP response"""
        keywords = []
        
        # Parse the JSON text content from MCP response
        try:
            import json
            if "content" in raw_data and raw_data["content"]:
                content_text = raw_data["content"][0].get("text", "{}")
                parsed_data = json.loads(content_text)
                items = parsed_data.get("items", [])
            else:
                items = []
            
            for item in items:
                # Extract data from DataForSEO Labs format
                keyword_info = item.get("keyword_info", {})
                keyword_props = item.get("keyword_properties", {})
                
                keyword_data = {
                    "keyword": item.get("keyword", ""),
                    "search_volume": keyword_info.get("search_volume", 0),
                    "difficulty": keyword_props.get("keyword_difficulty", 0),
                    "cpc": keyword_info.get("cpc", 0.0),
                    "competition": keyword_info.get("competition", 0.0),
                    "type": self._classify_keyword_type(item.get("keyword", ""))
                }
                keywords.append(keyword_data)
            
            return keywords
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error processing keyword data: {e}")
            return []
    
    def _process_serp_data(self, raw_data: Dict) -> List[Dict[str, Any]]:
        """Process raw SERP data from MCP response"""
        serp_results = []
        
        try:
            # Parse the JSON text content from MCP response
            if "content" in raw_data and raw_data["content"]:
                content_text = raw_data["content"][0].get("text", "{}")
                parsed_data = json.loads(content_text)
                items = parsed_data.get("items", [])
            else:
                items = []
            
            # Process various SERP item types
            position = 1
            for item in items:
                item_type = item.get("type", "")
                
                # Handle organic results
                if item_type == "organic":
                    result = {
                        "position": item.get("rank_absolute", position),
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "domain": item.get("domain", ""),
                        "type": "organic"
                    }
                    serp_results.append(result)
                    position += 1
                
                # Handle local pack results
                elif item_type == "local_pack":
                    result = {
                        "position": item.get("rank_absolute", position),
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "domain": item.get("domain", ""),
                        "type": "local_pack",
                        "rating": item.get("rating", {}).get("value", 0),
                        "phone": item.get("phone", "")
                    }
                    serp_results.append(result)
                    position += 1
                
                # Handle featured snippets
                elif item_type == "featured_snippet":
                    result = {
                        "position": 0,  # Featured snippets are always at the top
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("featured_title", ""),
                        "domain": item.get("domain", ""),
                        "type": "featured_snippet"
                    }
                    serp_results.append(result)
                
                # Add more types as needed (people_also_ask, video, etc.)
            
            # Sort by position and limit to top 10
            serp_results.sort(key=lambda x: x.get("position", 999))
            return serp_results[:10]
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error processing SERP data: {e}")
            return []
    
    def _classify_keyword_type(self, keyword: str) -> str:
        """Classify keyword type"""
        keyword_lower = keyword.lower()
        
        if any(q in keyword_lower for q in ["what", "how", "why", "when", "where"]):
            return "Question"
        elif any(c in keyword_lower for c in ["best", "top", "vs", "compare"]):
            return "Comparison"
        elif len(keyword.split()) >= 4:
            return "Long-tail"
        else:
            return "Related"
    
    def _generate_mock_keyword_data(self, seed_keyword: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock keyword data for development/testing"""
        import random
        
        prefixes = ["best", "top", "cheap", "affordable", "professional", "free"]
        suffixes = ["guide", "tutorial", "tips", "tools", "software", "reviews"]
        questions = ["what is", "how to", "why use", "when to use"]
        
        keywords = []
        
        # Add original keyword
        keywords.append({
            "keyword": seed_keyword,
            "search_volume": random.randint(1000, 50000),
            "difficulty": random.randint(30, 80),
            "cpc": round(random.uniform(1.0, 10.0), 2),
            "competition": round(random.uniform(0.3, 0.9), 2),
            "type": "Generic"
        })
        
        # Generate variations
        for i in range(min(limit - 1, 20)):
            if i < 6:  # Prefix variations
                keyword = f"{prefixes[i % len(prefixes)]} {seed_keyword}"
                kw_type = "Related"
            elif i < 12:  # Suffix variations
                keyword = f"{seed_keyword} {suffixes[i % len(suffixes)]}"
                kw_type = "Long-tail"
            else:  # Question variations
                keyword = f"{questions[i % len(questions)]} {seed_keyword}"
                kw_type = "Question"
            
            keywords.append({
                "keyword": keyword,
                "search_volume": random.randint(100, 10000),
                "difficulty": random.randint(10, 70),
                "cpc": round(random.uniform(0.5, 5.0), 2),
                "competition": round(random.uniform(0.1, 0.8), 2),
                "type": kw_type
            })
        
        return keywords[:limit]
    
    def _generate_mock_serp_data(self, keyword: str) -> List[Dict[str, Any]]:
        """Generate mock SERP data for development/testing"""
        return [
            {
                "position": 1,
                "title": f"Ultimate {keyword} Guide 2024 - Complete Tutorial",
                "url": f"https://example.com/{keyword.replace(' ', '-')}-guide",
                "description": f"Learn everything about {keyword} with our comprehensive guide. Expert tips, strategies, and best practices.",
                "domain": "example.com"
            },
            {
                "position": 2,
                "title": f"Top 10 {keyword} Tools & Software (2024 Updated)",
                "url": f"https://tools.com/best-{keyword.replace(' ', '-')}-tools",
                "description": f"Discover the best {keyword} tools and software. Compare features, pricing, and user reviews.",
                "domain": "tools.com"
            },
            {
                "position": 3,
                "title": f"{keyword} for Beginners: Step-by-Step Tutorial",
                "url": f"https://learn.com/{keyword.replace(' ', '-')}-beginners",
                "description": f"Start your {keyword} journey with this beginner-friendly tutorial. Easy to follow instructions.",
                "domain": "learn.com"
            }
        ]