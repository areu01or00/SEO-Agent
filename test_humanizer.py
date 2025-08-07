#!/usr/bin/env python3
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

# Set up environment
os.environ['DATAFORSEO_USERNAME'] = os.getenv('DATAFORSEO_USERNAME', '')
os.environ['DATAFORSEO_PASSWORD'] = os.getenv('DATAFORSEO_PASSWORD', '')
os.environ['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY', '')

from agents.content_generator import ContentGeneratorAgent

print('='*60)
print('TESTING HUMANIZER API WITH 3000-WORD CONTENT')
print('='*60)

# Step 1: Generate 3000-word blog post
print('\n1. GENERATING 3000-WORD BLOG POST...\n')
agent = ContentGeneratorAgent()
brief = {'keyword': 'digital marketing strategies'}
result = agent.generate_content(
    content_brief=brief,
    content_type='Blog Post',
    target_audience='business owners',
    title='Complete Guide to Digital Marketing Strategies in 2024',
    word_count=3000,
    use_mcp_research=False,
    tone='professional',
    readability_level='intermediate'
)

original_content = result['content']
original_word_count = len(original_content.split())
print(f'Generated: {original_word_count} words')
print(f'First 200 chars: {original_content[:200]}...')

# Step 2: Humanize using API
print('\n2. HUMANIZING CONTENT VIA API...\n')

# API credentials
email = 'info@bluemoonmarketing.com.au'
password = '6c90555bfd313691'
api_url = 'https://ai-text-humanizer.com/api/humanize'

# Prepare request
headers = {
    'Content-Type': 'application/json'
}

payload = {
    'email': email,
    'password': password,
    'text': original_content
}

print(f'Sending {len(original_content)} characters to Humanizer API...')

try:
    response = requests.post(api_url, json=payload, headers=headers, timeout=60)
    print(f'Response status: {response.status_code}')
    
    if response.status_code == 200:
        humanized_data = response.json()
        
        if 'humanizedText' in humanized_data:
            humanized_content = humanized_data['humanizedText']
            humanized_word_count = len(humanized_content.split())
            
            print(f'✅ Humanization successful!')
            print(f'Humanized: {humanized_word_count} words')
            print(f'First 200 chars: {humanized_content[:200]}...')
            
            # Step 3: Save both versions to files
            print('\n3. SAVING TO FILES...\n')
            
            # Save original
            with open('test_original.md', 'w') as f:
                f.write('# ORIGINAL AI CONTENT\n\n')
                f.write(f'Word Count: {original_word_count}\n\n')
                f.write(original_content)
            print('Saved original to: test_original.md')
            
            # Save humanized
            with open('test_humanized.md', 'w') as f:
                f.write('# HUMANIZED CONTENT\n\n')
                f.write(f'Word Count: {humanized_word_count}\n\n')
                f.write(humanized_content)
            print('Saved humanized to: test_humanized.md')
            
            # Step 4: Compare
            print('\n4. COMPARISON ANALYSIS:\n')
            print(f'Original words: {original_word_count}')
            print(f'Humanized words: {humanized_word_count}')
            word_change = ((humanized_word_count/original_word_count)-1)*100 if original_word_count > 0 else 0
            print(f'Word count change: {word_change:.1f}%')
            
            # Check if content is actually different
            if original_content != humanized_content:
                print('✅ Content successfully transformed')
                
                # Show sample differences
                orig_lines = original_content.split('\n')[:3]
                human_lines = humanized_content.split('\n')[:3]
                
                print('\nFirst 3 lines comparison:')
                print('ORIGINAL:')
                for line in orig_lines:
                    if line.strip():
                        print(f'  {line[:100]}...' if len(line) > 100 else f'  {line}')
                
                print('\nHUMANIZED:')
                for line in human_lines:
                    if line.strip():
                        print(f'  {line[:100]}...' if len(line) > 100 else f'  {line}')
            else:
                print('⚠️ Content unchanged')
                
        else:
            print(f'❌ API Response missing humanizedText')
            print(f'Response keys: {humanized_data.keys()}')
            print(f'Full response: {humanized_data}')
    else:
        print(f'❌ API returned status {response.status_code}')
        print(f'Response: {response.text}')
        
except requests.exceptions.RequestException as e:
    print(f'❌ API Request failed: {str(e)}')
    if hasattr(e, 'response') and e.response is not None:
        print(f'Response status: {e.response.status_code}')
        print(f'Response: {e.response.text}')
except Exception as e:
    print(f'❌ Error: {str(e)}')
    import traceback
    traceback.print_exc()

print('\n' + '='*60)
print('TEST COMPLETE')
print('='*60)