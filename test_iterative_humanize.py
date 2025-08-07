#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv
load_dotenv()

os.environ['DATAFORSEO_USERNAME'] = os.getenv('DATAFORSEO_USERNAME', '')
os.environ['DATAFORSEO_PASSWORD'] = os.getenv('DATAFORSEO_PASSWORD', '')
os.environ['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY', '')

from agents.content_generator import ContentGeneratorAgent
from utils.llm_client import LLMClient

print('TESTING ITERATIVE HUMANIZATION APPROACH')
print('='*60)

target_words = 3000
achieved_words = 0
final_content = []
iteration = 0
max_iterations = 5

# Initialize components
agent = ContentGeneratorAgent()
llm = LLMClient()
api_url = 'https://ai-text-humanizer.com/api.php'
api_creds = {
    'email': 'info@bluemoonmarketing.com.au',
    'pw': '6c90555bfd313691'
}

# Initial brief
brief = {'keyword': 'digital marketing strategies'}
title = 'Complete Digital Marketing Guide for 2024'
audience = 'business owners'

print(f'Target: {target_words} words\n')

while achieved_words < target_words and iteration < max_iterations:
    iteration += 1
    remaining = target_words - achieved_words
    
    print(f'ITERATION {iteration}:')
    print(f'  Current: {achieved_words} words')
    print(f'  Need: {remaining} more words')
    
    # Calculate how much to generate
    # Account for ~70% reduction during humanization
    chunk_target = int(remaining * 3.5)  # Generate 3.5x to get desired amount after humanization
    
    # Cap chunk size for API limits
    chunk_target = min(chunk_target, 5000)
    
    print(f'  Generating {chunk_target} words...')
    
    # Create continuation prompt if we have existing content
    if final_content:
        continuation_prompt = f"""Continue writing this blog post about {brief['keyword']}. 
        
Previous content ended with: ...{' '.join(final_content[-1].split()[-50:])}

Continue naturally from where it left off. Add new sections, examples, and insights.
Target length: {chunk_target} words."""
        
        # Generate continuation using LLM directly for better control
        new_chunk = llm.generate_text(
            continuation_prompt,
            max_tokens=chunk_target * 2,
            temperature=0.7
        )
    else:
        # First iteration - generate initial content
        result = agent.generate_content(
            content_brief=brief,
            content_type='Blog Post',
            target_audience=audience,
            title=title,
            word_count=chunk_target,
            use_mcp_research=False,
            tone='professional'
        )
        new_chunk = result['content']
    
    chunk_words = len(new_chunk.split())
    print(f'  Generated: {chunk_words} words')
    
    # Humanize the chunk
    print(f'  Humanizing...')
    payload = {**api_creds, 'text': new_chunk}
    
    try:
        response = requests.post(api_url, data=payload, timeout=60)
        if response.status_code == 200 and response.text:
            humanized_chunk = response.text.strip()
            humanized_words = len(humanized_chunk.split())
            print(f'  Humanized: {humanized_words} words')
            
            # Add to final content
            final_content.append(humanized_chunk)
            achieved_words += humanized_words
            
            reduction = ((chunk_words - humanized_words) / chunk_words) * 100
            print(f'  Reduction: {reduction:.1f}%')
        else:
            print(f'  ❌ Humanization failed')
            break
    except Exception as e:
        print(f'  ❌ Error: {e}')
        break
    
    print()

# Combine all chunks
print('='*60)
print('FINAL RESULTS:')
print(f'  Iterations: {iteration}')
print(f'  Total words: {achieved_words}')
print(f'  Target: {target_words}')
print(f'  Accuracy: {(achieved_words/target_words)*100:.1f}%')

if achieved_words >= target_words * 0.9:  # Within 90% of target
    print('  ✅ SUCCESS!')
else:
    print(f'  ⚠️ Short by {target_words - achieved_words} words')

# Save final content
final_text = '\n\n'.join(final_content)
with open('test_iterative_final.md', 'w', encoding='utf-8') as f:
    f.write(f'# ITERATIVELY HUMANIZED CONTENT\n\n')
    f.write(f'**Target:** {target_words} words\n')
    f.write(f'**Achieved:** {achieved_words} words\n')
    f.write(f'**Iterations:** {iteration}\n\n')
    f.write('---\n\n')
    f.write(final_text)

print(f'\n✅ Saved to test_iterative_final.md')

# Show structure
print('\nCONTENT STRUCTURE:')
for i, chunk in enumerate(final_content, 1):
    words = len(chunk.split())
    preview = chunk[:100].replace('\n', ' ')
    print(f'  Chunk {i}: {words} words - "{preview}..."')