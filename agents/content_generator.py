"""
Content Generator Agent for creating SEO-optimized content based on briefs
"""
import os
import math
import re
import requests
from typing import List, Dict, Any, Optional, Tuple
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
        use_mcp_research: bool = True,
        heading_structure: Dict[str, Any] = None,
        tone: str = "professional",
        readability_level: str = "intermediate"
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
                chat_history,
                heading_structure,
                tone,
                readability_level
            )
            
            # Generate content with appropriate token limit
            # Increased multiplier from 2 to 2.5 for better word count accuracy
            # Increased cap from 4000 to 6000 for longer content
            max_tokens = min(int(word_count * 2.5), 6000)  # Better token to word ratio
            
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
        chat_history: List[Dict[str, str]] = None,
        heading_structure: Dict[str, Any] = None,
        tone: str = "professional",
        readability_level: str = "intermediate"
    ) -> str:
        """Build sophisticated prompt for content generation with custom headings and humanization"""
        
        # Extract brief details
        brief_text = content_brief.get('brief', '')
        keyword = content_brief.get('keyword', '')
        
        # Build heading structure instructions
        heading_instructions = ""
        if heading_structure:
            heading_instructions = "\n\nHEADING STRUCTURE REQUIREMENTS:\n"
            if heading_structure.get('h1_count'):
                heading_instructions += f"- Use exactly {heading_structure['h1_count']} H1 heading (the title)\n"
            if heading_structure.get('h2_count'):
                heading_instructions += f"- Include {heading_structure['h2_count']} H2 sections\n"
                if heading_structure.get('h2_keywords'):
                    heading_instructions += f"  Keywords to include in H2s: {', '.join(heading_structure['h2_keywords'])}\n"
            if heading_structure.get('h3_count'):
                heading_instructions += f"- Include {heading_structure['h3_count']} H3 subsections per H2 section\n"
                if heading_structure.get('h3_keywords'):
                    heading_instructions += f"  Keywords to include in H3s: {', '.join(heading_structure['h3_keywords'])}\n"
        
        # Build tone and style instructions
        tone_instructions = self._get_tone_instructions(tone, readability_level)
        
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
        
        prompt = f"""You are an expert content writer specializing in creating humanized, SEO-optimized content.

ROLE: Create a {content_type} that sounds natural, engaging, and human-written while being optimized for search engines.

TARGET AUDIENCE: {target_audience}
TONE: {tone}
READABILITY LEVEL: {readability_level}

{tone_instructions}

CONTENT BRIEF:
{brief_text}

TITLE: {title}

TARGET WORD COUNT: {word_count} words (IMPORTANT: Generate AT LEAST {word_count} words)

{heading_instructions}

PRIMARY KEYWORD: {keyword}

{research_context}

{chat_context}

HUMANIZED WRITING GUIDELINES:
1. Use a {tone} tone that resonates with {target_audience}
2. Vary sentence length naturally (mix short, medium, and long sentences)
3. Include personal insights, analogies, or relatable examples
4. Use transitional phrases to create flow between paragraphs
5. Add rhetorical questions to engage readers
6. Include conversational elements like "you might wonder" or "here's the thing"
7. Use active voice predominantly (80%+)
8. Include specific examples and case studies where relevant
9. Add a personal touch with phrases like "In my experience" or "I've found that"
10. Use contractions naturally (it's, don't, you'll) for conversational flow

SEO OPTIMIZATION:
- Use the primary keyword "{keyword}" naturally 3-5 times
- Include related keywords and semantic variations
- Optimize headings with relevant keywords
- Create compelling meta-worthy opening paragraph

CONTENT STRUCTURE:
- Start with a hook that grabs attention
- Use the specified heading structure
- Include bullet points or numbered lists for scannability
- Add a clear call-to-action at the end
- Maintain approximately {word_count} words

IMPORTANT:
- Write like a human expert, not an AI
- Avoid robotic or formulaic language
- Don't use obvious AI phrases like "In this article, we will explore"
- Include natural imperfections like colloquialisms
- Focus on providing genuine value while maintaining readability

Now, generate the complete {content_type} content with a natural, human voice:"""
        
        return prompt
    
    def _get_tone_instructions(self, tone: str, readability_level: str) -> str:
        """Get specific instructions for tone and readability"""
        
        tone_map = {
            "professional": "Use industry-appropriate terminology while remaining accessible. Maintain authority without being stuffy.",
            "conversational": "Write as if having a friendly chat with the reader. Use 'you' and 'your' frequently. Include casual phrases.",
            "friendly": "Be warm and approachable. Use encouraging language and positive framing. Include personal touches.",
            "expert": "Demonstrate deep knowledge with confidence. Use technical terms when appropriate but explain complex concepts.",
            "casual": "Keep it light and easy-going. Use everyday language and relatable examples. Don't be afraid of humor.",
            "persuasive": "Use compelling arguments and emotional appeals. Include social proof and urgency where appropriate."
        }
        
        readability_map = {
            "simple": "Use short sentences (10-15 words average). Stick to common words. One idea per paragraph. 8th-grade reading level.",
            "intermediate": "Mix sentence lengths (15-20 words average). Use some industry terms with context. 10th-grade reading level.",
            "advanced": "Use sophisticated vocabulary and complex sentence structures where appropriate. College reading level."
        }
        
        instructions = f"""
TONE & STYLE REQUIREMENTS:
- Tone: {tone_map.get(tone, tone_map['professional'])}
- Readability: {readability_map.get(readability_level, readability_map['intermediate'])}
- Include personal pronouns (I, you, we) to create connection
- Use storytelling elements where appropriate
- Add personality without sacrificing professionalism
"""
        return instructions
    
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
        keyword: str = "",
        target_word_count: int = None
    ) -> str:
        """Refine existing content based on user feedback"""
        
        word_count_instruction = f"\n\nTARGET WORD COUNT: {target_word_count} words\nIMPORTANT: You MUST adjust the content length to be approximately {target_word_count} words. If current content is shorter, expand it. If longer, condense it." if target_word_count else ""
        
        prompt = f"""You are refining existing content based on user feedback.{word_count_instruction}

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
        
        # Calculate max_tokens based on target word count or current content
        if target_word_count:
            # Use target word count with same multiplier as main generation
            max_tokens = min(int(target_word_count * 2.5), 6000)
        else:
            # Fallback to current content length
            max_tokens = len(current_content.split()) * 2
        
        refined = self.llm_client.generate_text(
            prompt,
            max_tokens=max_tokens,
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
    
    def _parse_markdown_structure(self, content: str) -> List[Dict[str, Any]]:
        """Parse content to extract markdown structure with headings and body text"""
        sections = []
        lines = content.split('\n')
        current_section = {'heading': '', 'level': 0, 'body': [], 'raw_heading': ''}
        
        for line in lines:
            # Check if it's a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if heading_match:
                # Save previous section if it has content
                if current_section['body'] or current_section['heading']:
                    current_section['body'] = '\n'.join(current_section['body'])
                    sections.append(current_section)
                
                # Start new section
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2)
                current_section = {
                    'heading': heading_text,
                    'level': level,
                    'body': [],
                    'raw_heading': line  # Store the full markdown heading
                }
            else:
                # Add line to current section body
                current_section['body'].append(line)
        
        # Don't forget the last section
        if current_section['body'] or current_section['heading']:
            current_section['body'] = '\n'.join(current_section['body'])
            sections.append(current_section)
        
        return sections
    
    def _humanize_text_chunk(self, text: str, api_url: str, api_creds: dict) -> Tuple[str, bool, int, int]:
        """Humanize a single chunk of text"""
        original_words = len(text.split())
        
        payload = {**api_creds, 'text': text}
        
        try:
            response = requests.post(api_url, data=payload, timeout=30)
            if response.status_code == 200 and response.text:
                humanized = response.text.strip()
                humanized_words = len(humanized.split())
                return humanized, True, original_words, humanized_words
            else:
                return text, False, original_words, original_words
        except Exception as e:
            return text, False, original_words, original_words
    
    def humanize_ultra(self, content: str, target_word_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Humanize content while preserving markdown structure and headings
        Maintains 95-105% of original word count through expansion if needed
        
        Args:
            content: The content to humanize (with markdown formatting)
            target_word_count: Target word count (defaults to original length)
            
        Returns:
            Dict with humanized content and metadata
        """
        original_words = len(content.split())
        target_words = target_word_count or original_words
        
        # Parse markdown structure
        sections = self._parse_markdown_structure(content)
        
        # API configuration
        api_url = 'https://ai-text-humanizer.com/api.php'
        api_creds = {
            'email': 'info@bluemoonmarketing.com.au',
            'pw': '6c90555bfd313691'
        }
        
        # Process each section
        humanized_sections = []
        total_humanized_words = 0
        total_original_words = 0
        chunk_stats = []
        chunk_num = 0
        
        for section in sections:
            # Keep the heading as-is (don't humanize headings)
            humanized_section = {
                'raw_heading': section['raw_heading'],
                'heading': section['heading'],
                'level': section['level'],
                'body': ''
            }
            
            # Humanize the body text if it exists and has substantial content
            body_text = section['body'].strip()
            if body_text and len(body_text.split()) > 10:  # Only humanize if more than 10 words
                # Split body into chunks if it's too long
                body_words = body_text.split()
                chunk_size = 1000
                
                if len(body_words) > chunk_size:
                    # Process in chunks
                    humanized_parts = []
                    for i in range(0, len(body_words), chunk_size):
                        chunk_num += 1
                        chunk = ' '.join(body_words[i:i+chunk_size])
                        humanized_chunk, success, orig_words, human_words = self._humanize_text_chunk(
                            chunk, api_url, api_creds
                        )
                        humanized_parts.append(humanized_chunk)
                        total_original_words += orig_words
                        total_humanized_words += human_words
                        
                        chunk_stats.append({
                            'chunk': chunk_num,
                            'section': section['heading'] or 'Introduction',
                            'original': orig_words,
                            'humanized': human_words,
                            'reduction': ((orig_words - human_words) / orig_words * 100) if orig_words > 0 else 0,
                            'success': success
                        })
                    
                    humanized_section['body'] = ' '.join(humanized_parts)
                else:
                    # Process as single chunk
                    chunk_num += 1
                    humanized_body, success, orig_words, human_words = self._humanize_text_chunk(
                        body_text, api_url, api_creds
                    )
                    humanized_section['body'] = humanized_body
                    total_original_words += orig_words
                    total_humanized_words += human_words
                    
                    chunk_stats.append({
                        'chunk': chunk_num,
                        'section': section['heading'] or 'Introduction',
                        'original': orig_words,
                        'humanized': human_words,
                        'reduction': ((orig_words - human_words) / orig_words * 100) if orig_words > 0 else 0,
                        'success': success
                    })
            else:
                # Keep short sections as-is
                humanized_section['body'] = body_text
                if body_text:
                    words = len(body_text.split())
                    total_original_words += words
                    total_humanized_words += words
            
            humanized_sections.append(humanized_section)
        
        # Rebuild content with structure preserved
        rebuilt_content = []
        for section in humanized_sections:
            if section['raw_heading']:
                rebuilt_content.append(section['raw_heading'])
            if section['body']:
                rebuilt_content.append(section['body'])
        
        collated_content = '\n\n'.join(filter(None, rebuilt_content))
        
        # Calculate shortfall
        current_words = len(collated_content.split())
        shortfall = target_words - current_words
        
        # Expand if needed (if short by more than 100 words)
        final_content = collated_content
        final_words = current_words
        
        if shortfall > 100:
            # Get the last section for context
            last_section_text = humanized_sections[-1]['body'] if humanized_sections else ""
            sample_text = last_section_text[-500:] if len(last_section_text) > 500 else last_section_text
            
            expansion_prompt = f'''Continue this humanized content by adding approximately {shortfall} more words.

CRITICAL: Match this exact writing style (simple, direct, short sentences):
{sample_text[:300] if sample_text else "Write in a simple, direct style with short sentences."}

The content currently ends with:
...{collated_content[-500:]}

Continue from where it left off and add {shortfall} more words. Keep the same simple, direct style with short sentences.
Maintain the professional tone and topic focus.

Continue the content:'''
            
            additional_content = self.llm_client.generate_text(
                expansion_prompt,
                max_tokens=int(shortfall * 2),
                temperature=0.7
            )
            
            # Add expansion as a new section or continuation
            final_content = collated_content + "\n\n" + additional_content
            final_words = len(final_content.split())
        
        # Calculate final statistics
        accuracy = (final_words / target_words) * 100
        
        return {
            'content': final_content,
            'metadata': {
                'original_words': original_words,
                'target_words': target_words,
                'humanized_words': total_humanized_words,
                'final_words': final_words,
                'chunks_processed': chunk_num,
                'sections_processed': len(sections),
                'accuracy_percentage': round(accuracy, 1),
                'chunk_stats': chunk_stats,
                'expanded': shortfall > 100,
                'expansion_words': final_words - current_words if shortfall > 100 else 0,
                'humanized': True,
                'structure_preserved': True
            }
        }