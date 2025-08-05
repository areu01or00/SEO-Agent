"""
Content Generator Agent for creating SEO-optimized content based on briefs
"""
import os
from typing import List, Dict, Any, Optional
from utils.llm_client import LLMClient
# MCP client import moved to __init__ method
import json

class ContentGeneratorAgent:
    """
    Advanced content generation agent with REST API integration for real-time data
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        from mcp.client import DataForSEOMCP
        self.dataforseo_mcp = DataForSEOMCP()  # Using MCP client
        self.content_templates = self._load_content_templates()
        
    def _load_content_templates(self) -> Dict[str, str]:
        """Load content structure templates for different content types"""
        return {
            "Blog Post": """
# {title}

## Introduction
{introduction}

## {section_1_title}
{section_1_content}

## {section_2_title}
{section_2_content}

## {section_3_title}
{section_3_content}

## Key Takeaways
{key_takeaways}

## Conclusion
{conclusion}
""",
            "Landing Page": """
# {headline}

## {value_proposition}

### Benefits
{benefits}

### Features
{features}

### How It Works
{how_it_works}

### Testimonials
{testimonials}

### Call to Action
{cta}
""",
            "Product Page": """
# {product_name}

## Product Overview
{overview}

## Key Features
{features}

## Specifications
{specifications}

## Benefits
{benefits}

## Customer Reviews
{reviews}

## Pricing
{pricing}

## Call to Action
{cta}
""",
            "Guide/Tutorial": """
# {title}

## What You'll Learn
{objectives}

## Prerequisites
{prerequisites}

## Step 1: {step_1_title}
{step_1_content}

## Step 2: {step_2_title}
{step_2_content}

## Step 3: {step_3_title}
{step_3_content}

## Common Issues & Solutions
{troubleshooting}

## Summary
{summary}

## Next Steps
{next_steps}
""",
            "Comparison Article": """
# {title}

## Quick Comparison Table
{comparison_table}

## Overview
{overview}

## {option_1_name} Review
### Pros
{option_1_pros}
### Cons
{option_1_cons}
### Best For
{option_1_best_for}

## {option_2_name} Review
### Pros
{option_2_pros}
### Cons
{option_2_cons}
### Best For
{option_2_best_for}

## Final Verdict
{verdict}

## Recommendation
{recommendation}
"""
        }
    
    def generate_content(
        self,
        content_brief: Dict[str, Any],
        content_type: str,
        target_audience: str,
        title: str,
        word_count: int,
        chat_history: List[Dict[str, str]] = None,
        use_mcp_research: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive content based on brief and parameters
        
        Args:
            content_brief: The full content brief from Tab 7
            content_type: Type of content (Blog Post, Landing Page, etc.)
            target_audience: Target audience description
            title: Selected or custom title
            word_count: Target word count
            chat_history: Previous chat messages for context
            use_mcp_research: Whether to use MCP tools for additional research
        
        Returns:
            Dictionary with generated content and metadata
        """
        try:
            # Gather additional research if enabled
            research_data = {}
            if use_mcp_research:
                research_data = self._gather_mcp_research(
                    content_brief.get('keyword', ''),
                    title
                )
            
            # Build comprehensive prompt
            prompt = self._build_content_prompt(
                content_brief,
                content_type,
                target_audience,
                title,
                word_count,
                research_data,
                chat_history
            )
            
            # Generate content with appropriate token limit
            max_tokens = min(word_count * 2, 4000)  # Approximate token to word ratio
            
            generated_content = self.llm_client.generate_text(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            # Post-process content
            processed_content = self._post_process_content(
                generated_content,
                content_type,
                title
            )
            
            return {
                'content': processed_content,
                'metadata': {
                    'title': title,
                    'type': content_type,
                    'audience': target_audience,
                    'word_count': len(processed_content.split()),
                    'research_used': bool(research_data)
                },
                'research_data': research_data
            }
            
        except Exception as e:
            print(f"Content generation error: {str(e)}")
            return {
                'content': f"# {title}\n\nContent generation failed. Please try again.",
                'metadata': {'error': str(e)},
                'research_data': {}
            }
    
    def _gather_mcp_research(self, keyword: str, title: str) -> Dict[str, Any]:
        """Use MCP tools to gather real-time data for content enhancement"""
        research = {}
        
        try:
            # Get current SERP data for competitive insights
            serp_data = self.dataforseo_mcp.get_serp_analysis(keyword)
            if serp_data:
                research['competitor_insights'] = [
                    {
                        'title': item.get('title', ''),
                        'description': item.get('description', '')
                    }
                    for item in serp_data[:3]
                ]
            
            # Get related keywords for semantic richness
            related_keywords = self.dataforseo_mcp.get_keyword_suggestions(
                keyword, 
                limit=10
            )
            if related_keywords:
                research['related_terms'] = [
                    kw.get('keyword', '') 
                    for kw in related_keywords[:5]
                ]
            
            # Get trends data for timely content
            trends = self.dataforseo_mcp.get_trends_data([keyword])
            if trends and trends.get('graph_data'):
                # Check if trending up or down
                data_points = trends['graph_data']
                if len(data_points) > 2:
                    # Safely get values from data points
                    last_point = data_points[-1] if isinstance(data_points[-1], dict) else {'value': 0}
                    prev_point = data_points[-3] if isinstance(data_points[-3], dict) else {'value': 0}
                    recent_trend = last_point.get('value', 0) - prev_point.get('value', 0)
                    research['trending'] = 'up' if recent_trend > 0 else 'stable'
            
        except Exception as e:
            print(f"MCP research error: {str(e)}")
        
        return research
    
    def _build_content_prompt(
        self,
        content_brief: Dict[str, Any],
        content_type: str,
        target_audience: str,
        title: str,
        word_count: int,
        research_data: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Build sophisticated prompt for content generation"""
        
        # Extract brief details
        brief_text = content_brief.get('brief', '')
        keyword = content_brief.get('keyword', '')
        
        # Build research context
        research_context = ""
        if research_data:
            if research_data.get('competitor_insights'):
                research_context += "\nCompetitor Content Insights:\n"
                for comp in research_data['competitor_insights']:
                    research_context += f"- {comp['title']}\n"
            
            if research_data.get('related_terms'):
                research_context += f"\nRelated Keywords to Include: {', '.join(research_data['related_terms'])}\n"
            
            if research_data.get('trending'):
                research_context += f"\nTrend Status: This topic is currently {research_data['trending']}\n"
        
        # Build chat context
        chat_context = ""
        if chat_history:
            chat_context = "\nPrevious Instructions:\n"
            for msg in chat_history[-3:]:  # Last 3 messages for context
                if msg['role'] == 'user':
                    chat_context += f"User: {msg['content']}\n"
        
        prompt = f"""You are an expert content writer specializing in SEO-optimized, engaging content.

ROLE: Create a {content_type} that is informative, engaging, and optimized for search engines.

TARGET AUDIENCE: {target_audience}

CONTENT BRIEF:
{brief_text}

TITLE: {title}

TARGET WORD COUNT: {word_count} words

CONTENT TYPE STRUCTURE: {content_type}
{self.content_templates.get(content_type, '')}

PRIMARY KEYWORD: {keyword}

{research_context}

{chat_context}

WRITING GUIDELINES:
1. Write in a conversational yet professional tone appropriate for {target_audience}
2. Use the primary keyword naturally 3-5 times throughout the content
3. Include related keywords and semantic variations naturally
4. Create compelling headers and subheaders
5. Use short paragraphs (2-3 sentences) for better readability
6. Include actionable insights and practical examples
7. Add statistics or data points where relevant (you can use placeholder like [stat needed])
8. End with a strong call-to-action appropriate for the content type
9. Maintain approximately {word_count} words

IMPORTANT:
- Do NOT use generic filler content
- Do NOT keyword stuff
- Focus on providing genuine value to the reader
- Make the content scannable with proper formatting
- Use markdown formatting for headers, lists, and emphasis

Now, generate the complete {content_type} content:"""
        
        return prompt
    
    def _post_process_content(self, content: str, content_type: str, title: str) -> str:
        """Post-process generated content for quality and formatting"""
        
        # Ensure title is present
        if not content.startswith('#'):
            content = f"# {title}\n\n{content}"
        
        # Clean up any placeholder markers
        content = content.replace('[stat needed]', '(industry research shows)')
        content = content.replace('[source]', '')
        
        # Ensure proper markdown formatting
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Fix header formatting
            if line.strip() and not line.startswith('#') and line.isupper():
                line = f"## {line.title()}"
            
            # Add spacing around headers
            if line.startswith('#'):
                if processed_lines and processed_lines[-1].strip():
                    processed_lines.append('')
                processed_lines.append(line)
                processed_lines.append('')
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines).strip()
    
    def refine_content(
        self,
        current_content: str,
        refinement_instruction: str,
        keyword: str = ""
    ) -> str:
        """Refine existing content based on user feedback"""
        
        prompt = f"""You are refining existing content based on user feedback.

CURRENT CONTENT:
{current_content}

REFINEMENT INSTRUCTION:
{refinement_instruction}

{f"PRIMARY KEYWORD TO MAINTAIN: {keyword}" if keyword else ""}

Please revise the content according to the instruction while:
1. Maintaining the overall structure and key points
2. Keeping SEO optimization intact
3. Preserving the target audience focus
4. Ensuring the refined version is coherent and complete

Provide the refined content:"""
        
        refined = self.llm_client.generate_text(
            prompt,
            max_tokens=len(current_content.split()) * 2,
            temperature=0.5
        )
        
        return self._post_process_content(refined, "", "")
    
    def suggest_improvements(self, content: str) -> List[str]:
        """Suggest improvements for the generated content"""
        
        # Take more content for better analysis (2000 chars instead of 1000)
        content_snippet = content[:2000] if len(content) > 2000 else content
        
        prompt = f"""Analyze this content and provide 5 specific, actionable improvement suggestions:

{content_snippet}{"..." if len(content) > 2000 else ""}

Provide ONE concise suggestion for each area (keep each under 100 words):
1. SEO optimization - keyword usage and search visibility
2. Readability and engagement - tone, formatting, user experience  
3. Content structure - organization, headings, flow
4. Call-to-action effectiveness - conversion elements
5. Target audience appeal - relevance and resonance

Format each suggestion as:
[Area]: [Specific actionable suggestion]

Be specific and practical. Avoid generic advice."""
        
        suggestions = self.llm_client.generate_text(
            prompt,
            max_tokens=800,  # Increased from 500 to prevent cutoff
            temperature=0.3
        )
        
        # Parse suggestions into list
        suggestion_list = []
        for line in suggestions.split('\n'):
            if line.strip().startswith(('•', '-', '*', '1', '2', '3', '4', '5')):
                suggestion_list.append(line.strip().lstrip('•-*123456789. '))
        
        return suggestion_list if suggestion_list else ["Consider adding more specific examples", "Include relevant statistics", "Strengthen the call-to-action"]