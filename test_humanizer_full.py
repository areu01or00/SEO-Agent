#!/usr/bin/env python3
import os
import requests
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

# API credentials - CORRECT endpoint and parameters
email = 'info@bluemoonmarketing.com.au'
password = '6c90555bfd313691'
api_url = 'https://ai-text-humanizer.com/api.php'  # Correct endpoint

# Use form data (not JSON)
payload = {
    'email': email,
    'pw': password,  # Correct parameter name
    'text': original_content
}

print(f'Sending {len(original_content)} characters to Humanizer API...')

try:
    response = requests.post(api_url, data=payload, timeout=60)
    print(f'Response status: {response.status_code}')
    
    if response.status_code == 200 and response.text:
        # API returns humanized text directly, not JSON
        humanized_content = response.text.strip()
        humanized_word_count = len(humanized_content.split())
        
        print(f'✅ Humanization successful!')
        print(f'Humanized: {humanized_word_count} words')
        print(f'First 200 chars: {humanized_content[:200]}...')
        
        # Step 3: Save both versions to files
        print('\n3. SAVING TO FILES...\n')
        
        # Save original
        with open('test_original.md', 'w', encoding='utf-8') as f:
            f.write('# ORIGINAL AI CONTENT\n\n')
            f.write(f'**Word Count:** {original_word_count}\n\n')
            f.write('---\n\n')
            f.write(original_content)
        print('✅ Saved original to: test_original.md')
        
        # Save humanized
        with open('test_humanized.md', 'w', encoding='utf-8') as f:
            f.write('# HUMANIZED CONTENT\n\n')
            f.write(f'**Word Count:** {humanized_word_count}\n\n')
            f.write('---\n\n')
            f.write(humanized_content)
        print('✅ Saved humanized to: test_humanized.md')
        
        # Step 4: Compare
        print('\n4. COMPARISON ANALYSIS:\n')
        print(f'Original words: {original_word_count}')
        print(f'Humanized words: {humanized_word_count}')
        word_change = ((humanized_word_count/original_word_count)-1)*100 if original_word_count > 0 else 0
        print(f'Word count change: {word_change:.1f}%')
        
        # Check character count change
        orig_chars = len(original_content)
        human_chars = len(humanized_content)
        char_change = ((human_chars/orig_chars)-1)*100 if orig_chars > 0 else 0
        print(f'Character change: {char_change:.1f}%')
        
        # Show sample differences
        print('\n5. CONTENT COMPARISON (First paragraph):\n')
        
        # Get first meaningful paragraph from each
        orig_paras = [p.strip() for p in original_content.split('\n\n') if p.strip() and not p.startswith('#')]
        human_paras = [p.strip() for p in humanized_content.split('\n\n') if p.strip() and not p.startswith('#')]
        
        if orig_paras:
            print('ORIGINAL:')
            print('-' * 40)
            print(orig_paras[0][:300] + '...' if len(orig_paras[0]) > 300 else orig_paras[0])
        
        if human_paras:
            print('\nHUMANIZED:')
            print('-' * 40)
            print(human_paras[0][:300] + '...' if len(human_paras[0]) > 300 else human_paras[0])
        
        print('\n✅ Both files saved successfully. You can now review:')
        print('   - test_original.md (AI generated)')
        print('   - test_humanized.md (Humanized version)')
        
    else:
        print(f'❌ API returned status {response.status_code} or empty response')
        print(f'Response: {response.text[:500] if response.text else "Empty"}')
        
except requests.exceptions.RequestException as e:
    print(f'❌ API Request failed: {str(e)}')
    if hasattr(e, 'response') and e.response is not None:
        print(f'Response status: {e.response.status_code}')
        print(f'Response: {e.response.text[:500]}')
except Exception as e:
    print(f'❌ Error: {str(e)}')
    import traceback
    traceback.print_exc()

print('\n' + '='*60)
print('TEST COMPLETE')
print('='*60)