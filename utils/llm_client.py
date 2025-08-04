import os
import requests
import json
from typing import Optional, Dict, Any

class LLMClient:
    """
    Client for interacting with LLMs via OpenRouter/LiteLLM
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        """
        Generate text using the specified LLM model
        """
        try:
            # Use specified model or default
            model_to_use = model or self.model
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://bmm-seo-agent.com",  # Optional
                "X-Title": "BMM SEO Agent"  # Optional
            }
            
            data = {
                "model": model_to_use,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # Make request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract generated text
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise Exception("No content generated")
                
        except requests.exceptions.RequestException as e:
            print(f"OpenRouter API error: {str(e)}")
            return self._fallback_response(prompt)
        except Exception as e:
            print(f"LLM generation error: {str(e)}")
            return self._fallback_response(prompt)
    
    def analyze_keywords(
        self,
        keywords: list,
        seed_keyword: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze keywords using LLM for insights and clustering
        """
        try:
            # Prepare keywords text
            keywords_text = "\n".join([
                f"- {kw.get('keyword', '')} (Volume: {kw.get('search_volume', 0)}, Difficulty: {kw.get('difficulty', 0)})"
                for kw in keywords[:20]  # Limit to top 20 for analysis
            ])
            
            prompt = f"""
            You are an SEO expert analyzing keywords for "{seed_keyword}".
            
            Keywords to analyze:
            {keywords_text}
            
            {context}
            
            Please provide:
            1. Top 3 keyword opportunities (highest potential with reasonable difficulty)
            2. Content gap analysis
            3. Keyword clustering by intent (informational, commercial, navigational)
            4. Recommendations for content strategy
            
            Format your response as clear, actionable insights.
            """
            
            analysis = self.generate_text(prompt, max_tokens=1500, temperature=0.3)
            
            return {
                "analysis": analysis,
                "opportunities": self._extract_opportunities(analysis),
                "clusters": self._extract_clusters(keywords),
                "strategy": self._extract_strategy(analysis)
            }
            
        except Exception as e:
            return {
                "analysis": "Analysis temporarily unavailable.",
                "opportunities": [],
                "clusters": {},
                "strategy": "Focus on long-tail keywords with lower competition."
            }
    
    def generate_content_brief(
        self,
        keyword: str,
        serp_results: list,
        target_audience: str = "general"
    ) -> str:
        """
        Generate a content brief based on keyword and SERP analysis
        """
        try:
            # Prepare SERP context
            serp_text = "\n".join([
                f"- {result.get('title', '')} ({result.get('url', '')})"
                for result in serp_results[:5]
            ])
            
            prompt = f"""
            Create a content brief for the keyword "{keyword}" targeting {target_audience} audience.
            
            Current top-ranking pages:
            {serp_text}
            
            Please provide:
            1. Content title suggestions (3 options)
            2. Key topics to cover
            3. Content structure outline
            4. Word count recommendation
            5. Content angle to differentiate from competitors
            6. Call-to-action suggestions
            
            Make the brief practical and actionable for content creators.
            """
            
            brief = self.generate_text(prompt, max_tokens=1200, temperature=0.5)
            return brief
            
        except Exception as e:
            return f"Content brief for '{keyword}': Focus on comprehensive, user-focused content that addresses search intent better than current top results."
    
    def _extract_opportunities(self, analysis: str) -> list:
        """Extract top opportunities from analysis text"""
        # Simple extraction - in production, could use more sophisticated parsing
        opportunities = []
        lines = analysis.split('\n')
        
        for line in lines:
            if 'opportunity' in line.lower() or 'recommend' in line.lower():
                opportunities.append(line.strip())
        
        return opportunities[:3]
    
    def _extract_clusters(self, keywords: list) -> Dict[str, list]:
        """Simple keyword clustering by type"""
        clusters = {
            "informational": [],
            "commercial": [],
            "navigational": [],
            "other": []
        }
        
        for kw in keywords:
            keyword_text = kw.get('keyword', '').lower()
            
            if any(word in keyword_text for word in ['what', 'how', 'why', 'guide', 'tutorial']):
                clusters["informational"].append(kw['keyword'])
            elif any(word in keyword_text for word in ['buy', 'price', 'cost', 'cheap', 'best', 'review']):
                clusters["commercial"].append(kw['keyword'])
            elif any(word in keyword_text for word in ['login', 'download', 'site:', 'brand']):
                clusters["navigational"].append(kw['keyword'])
            else:
                clusters["other"].append(kw['keyword'])
        
        return clusters
    
    def _extract_strategy(self, analysis: str) -> str:
        """Extract strategy recommendations from analysis"""
        lines = analysis.split('\n')
        strategy_lines = []
        
        for line in lines:
            if any(word in line.lower() for word in ['strategy', 'recommend', 'focus', 'should']):
                strategy_lines.append(line.strip())
        
        return ' '.join(strategy_lines) if strategy_lines else "Focus on long-tail keywords with lower competition and clear user intent."
    
    def _fallback_response(self, prompt: str) -> str:
        """Provide fallback response when LLM is unavailable"""
        if "keyword" in prompt.lower():
            return "Keywords show good potential for content creation. Focus on long-tail variations with lower competition."
        elif "serp" in prompt.lower():
            return "SERP analysis shows opportunities for more comprehensive content addressing user intent."
        elif "content" in prompt.lower():
            return "Create comprehensive, user-focused content that provides more value than current top results."
        else:
            return "Analysis temporarily unavailable. Please try again later."
    
    def get_available_models(self) -> list:
        """Get list of available models from OpenRouter"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            models = response.json()
            
            # Return model IDs
            return [model.get("id", "") for model in models.get("data", [])]
            
        except Exception as e:
            # Return default models
            return [
                "google/gemini-2.5-flash-lite",
                "anthropic/claude-3-haiku",
                "openai/gpt-4o-mini",
                "meta-llama/llama-3.2-3b-instruct"
            ]