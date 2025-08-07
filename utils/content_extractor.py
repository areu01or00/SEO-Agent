"""
Content extraction fallback using Trafilatura for protected sites
"""
import trafilatura
from trafilatura import fetch_url, extract, extract_metadata
import re
import html
from typing import Dict, List, Any, Optional
from utils.llm_client import LLMClient

class ContentExtractor:
    """Extract and analyze content using Trafilatura when DataForSEO fails"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract content and SEO elements from URL using Trafilatura
        
        Args:
            url: URL to analyze
            
        Returns:
            Dict with extracted content and SEO metrics
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            print(f"🔄 Using Trafilatura to extract content from {url}")
            
            # Fetch the page
            downloaded = fetch_url(url)
            
            if not downloaded:
                print(f"❌ Failed to fetch {url}")
                return None
            
            # Extract metadata
            metadata = extract_metadata(downloaded)
            
            # Extract headings using regex
            h1_tags = self._extract_headings(downloaded, 'h1')
            h2_tags = self._extract_headings(downloaded, 'h2')
            h3_tags = self._extract_headings(downloaded, 'h3')
            
            # Extract main content
            content = extract(downloaded, include_comments=False, include_tables=True)
            
            # Extract meta description
            meta_desc = self._extract_meta_description(downloaded)
            
            # Calculate metrics
            word_count = len(content.split()) if content else 0
            
            # Extract links
            internal_links = len(re.findall(r'href=["\'](?:https?://)?(?:www\.)?bluemoonmarketing\.com\.au', downloaded, re.IGNORECASE))
            external_links = len(re.findall(r'href=["\']https?://(?!(?:www\.)?bluemoonmarketing\.com\.au)', downloaded, re.IGNORECASE))
            
            # Extract images
            images = len(re.findall(r'<img\s+[^>]*src=["\']', downloaded, re.IGNORECASE))
            
            # Build result structure matching DataForSEO format
            result = {
                'url': url,
                'title': metadata.title if metadata else '',
                'meta_description': meta_desc or (metadata.description if metadata else ''),
                'h1_tags': h1_tags[:5],  # Limit to 5
                'h2_tags': h2_tags[:10],  # Limit to 10
                'h3_tags': h3_tags[:10],  # Limit to 10
                'word_count': word_count,
                'internal_links': internal_links,
                'external_links': external_links,
                'images': images,
                'text_content': len(content) if content else 0,
                'onpage_score': self._calculate_onpage_score(metadata, h1_tags, meta_desc, word_count),
                'page_size': len(downloaded),
                'load_time': 0,  # Can't measure without browser
                'seo_checks': {
                    'has_https': url.startswith('https://'),
                    'has_title': bool(metadata and metadata.title),
                    'has_description': bool(meta_desc or (metadata and metadata.description)),
                    'has_favicon': bool(re.search(r'<link[^>]*rel=["\'](?:shortcut )?icon["\']', downloaded, re.IGNORECASE)),
                    'seo_friendly_url': self._check_seo_friendly_url(url),
                    'has_h1_tag': len(h1_tags) > 0,
                    'has_canonical': bool(re.search(r'<link[^>]*rel=["\']canonical["\']', downloaded, re.IGNORECASE))
                },
                'readability': {
                    'flesch_kincaid': 0,  # Would need text analysis
                    'automated_readability': 0,
                    'coleman_liau': 0,
                    'dale_chall': 0,
                    'smog': 0
                },
                'performance': {
                    'time_to_interactive': 0,
                    'dom_complete': 0,
                    'connection_time': 0,
                    'download_time': 0
                },
                'extraction_method': 'trafilatura',
                'content_text': content[:1000] if content else ''  # First 1000 chars for AI analysis
            }
            
            print(f"✅ Successfully extracted content using Trafilatura")
            return result
            
        except Exception as e:
            print(f"❌ Trafilatura extraction failed: {str(e)}")
            return None
    
    def _extract_headings(self, html_content: str, tag: str) -> List[str]:
        """Extract and clean heading tags"""
        pattern = f'<{tag}[^>]*>(.*?)</{tag}>'
        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        # Clean up matches
        cleaned = []
        for match in matches:
            # Remove nested HTML tags
            clean_text = re.sub(r'<[^>]+>', '', match)
            # Unescape HTML entities
            clean_text = html.unescape(clean_text.strip())
            # Remove extra whitespace
            clean_text = ' '.join(clean_text.split())
            if clean_text:
                cleaned.append(clean_text)
        
        return cleaned
    
    def _extract_meta_description(self, html_content: str) -> Optional[str]:
        """Extract meta description from HTML"""
        # Try different meta description patterns
        patterns = [
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
            r'<meta\s+content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
            r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']*)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return html.unescape(match.group(1))
        
        return None
    
    def _check_seo_friendly_url(self, url: str) -> bool:
        """Check if URL is SEO friendly"""
        # Remove protocol and domain
        path = re.sub(r'https?://[^/]+', '', url)
        
        # SEO unfriendly patterns
        unfriendly_patterns = [
            r'\?id=\d+',  # Query parameters with IDs
            r'[A-Z]{3,}',  # All caps
            r'_+',  # Multiple underscores
            r'[^\w\-/]',  # Special characters except dash and slash
        ]
        
        for pattern in unfriendly_patterns:
            if re.search(pattern, path):
                return False
        
        return True
    
    def _calculate_onpage_score(self, metadata, h1_tags: List[str], meta_desc: str, word_count: int) -> float:
        """Calculate a basic on-page SEO score"""
        score = 50.0  # Base score
        
        # Title exists and length
        if metadata and metadata.title:
            score += 10
            title_len = len(metadata.title)
            if 30 <= title_len <= 60:
                score += 5
        
        # Meta description exists and length
        if meta_desc:
            score += 10
            desc_len = len(meta_desc)
            if 120 <= desc_len <= 160:
                score += 5
        
        # H1 tag exists
        if h1_tags:
            score += 10
        
        # Word count
        if word_count >= 300:
            score += 5
        if word_count >= 1000:
            score += 5
        
        return min(score, 100.0)
    
    def generate_ai_insights(self, content_data: Dict[str, Any]) -> str:
        """Generate AI insights for the extracted content"""
        prompt = f"""Analyze this website content and provide SEO insights:

Title: {content_data.get('title', 'N/A')}
Meta Description: {content_data.get('meta_description', 'N/A')}
H1 Tags: {', '.join(content_data.get('h1_tags', [])[:3])}
H2 Tags: {', '.join(content_data.get('h2_tags', [])[:5])}
Word Count: {content_data.get('word_count', 0)}
Content Preview: {content_data.get('content_text', '')[:500]}

Provide 3 actionable SEO recommendations in a concise format."""

        try:
            insights = self.llm_client.generate_text(prompt, max_tokens=500, temperature=0.3)
            return insights
        except:
            return "AI insights unavailable"