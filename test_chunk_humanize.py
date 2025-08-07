#!/usr/bin/env python3
import os
import requests
import math
from dotenv import load_dotenv
load_dotenv()

os.environ['DATAFORSEO_USERNAME'] = os.getenv('DATAFORSEO_USERNAME', '')
os.environ['DATAFORSEO_PASSWORD'] = os.getenv('DATAFORSEO_PASSWORD', '')
os.environ['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY', '')

from agents.content_generator import ContentGeneratorAgent
from utils.llm_client import LLMClient

print('TESTING CHUNK-BY-CHUNK HUMANIZATION WITH EXPANSION')
print('='*60)

# Step 1: Generate original content
print('\n1. GENERATING ORIGINAL CONTENT (3000 words)...\n')
agent = ContentGeneratorAgent()
brief = {'keyword': 'digital marketing strategies'}
result = agent.generate_content(
    content_brief=brief,
    content_type='Blog Post',
    target_audience='business owners',
    title='Complete Digital Marketing Guide 2024',
    word_count=3000,
    use_mcp_research=False,
    tone='professional'
)

original_content = result['content']
original_words = len(original_content.split())
print(f'✅ Generated: {original_words} words')

# Step 2: Split into chunks
print('\n2. SPLITTING INTO CHUNKS...\n')
words = original_content.split()
chunk_size = 1000
num_chunks = math.ceil(len(words) / chunk_size)

chunks = []
for i in range(num_chunks):
    start = i * chunk_size
    end = min((i + 1) * chunk_size, len(words))
    chunk = ' '.join(words[start:end])
    chunks.append(chunk)
    print(f'  Chunk {i+1}: {len(chunk.split())} words')

# Step 3: Humanize each chunk
print('\n3. HUMANIZING EACH CHUNK...\n')
api_url = 'https://ai-text-humanizer.com/api.php'
api_creds = {
    'email': 'info@bluemoonmarketing.com.au',
    'pw': '6c90555bfd313691'
}

humanized_chunks = []
total_humanized_words = 0

for i, chunk in enumerate(chunks, 1):
    print(f'  Processing chunk {i}/{num_chunks}...')
    chunk_words = len(chunk.split())
    
    payload = {**api_creds, 'text': chunk}
    
    try:
        response = requests.post(api_url, data=payload, timeout=30)
        if response.status_code == 200 and response.text:
            humanized = response.text.strip()
            humanized_words = len(humanized.split())
            humanized_chunks.append(humanized)
            total_humanized_words += humanized_words
            
            reduction = ((chunk_words - humanized_words) / chunk_words) * 100
            print(f'    Original: {chunk_words} → Humanized: {humanized_words} (reduced {reduction:.0f}%)')
        else:
            print(f'    ❌ Failed to humanize chunk {i}')
            humanized_chunks.append(chunk)  # Keep original if fail
            total_humanized_words += chunk_words
    except Exception as e:
        print(f'    ❌ Error: {e}')
        humanized_chunks.append(chunk)
        total_humanized_words += chunk_words

# Step 4: Collate humanized chunks
print('\n4. COLLATING HUMANIZED CONTENT...\n')
collated_content = '\n\n'.join(humanized_chunks)
print(f'  Total humanized words: {total_humanized_words}')
print(f'  Target was: {original_words}')
shortfall = original_words - total_humanized_words

# Step 5: Expand if needed
if shortfall > 100:  # If short by more than 100 words
    print(f'\n5. EXPANDING CONTENT (need {shortfall} more words)...\n')
    
    llm = LLMClient()
    
    # Get a sample of humanized style
    sample_humanized = humanized_chunks[0][:500] if humanized_chunks else ""
    
    expansion_prompt = f'''Continue this humanized blog post by adding approximately {shortfall} more words.

CRITICAL: Match this exact writing style (simple, direct, short sentences):
{sample_humanized}

The blog post currently ends with:
...{collated_content[-500:]}

Continue from where it left off and add {shortfall} more words. Keep the same simple, direct style with short sentences.

Continue the blog post:'''
    
    additional_content = llm.generate_text(
        expansion_prompt,
        max_tokens=int(shortfall * 2),
        temperature=0.7
    )
    
    final_content = collated_content + "\n\n" + additional_content
    final_words = len(final_content.split())
    
    print(f'  ✅ Expanded to: {final_words} words')
else:
    print('\n5. NO EXPANSION NEEDED\n')
    final_content = collated_content
    final_words = total_humanized_words

# Step 6: Save results
print('\n6. SAVING RESULTS...\n')

# Save final version
with open('test_chunk_humanized_final.md', 'w', encoding='utf-8') as f:
    f.write('# CHUNK-BY-CHUNK HUMANIZED CONTENT\n\n')
    f.write('## Process Summary\n\n')
    f.write(f'- **Original:** {original_words} words\n')
    f.write(f'- **After humanization:** {total_humanized_words} words\n')
    f.write(f'- **After expansion:** {final_words} words\n')
    f.write(f'- **Chunks processed:** {num_chunks}\n\n')
    f.write('---\n\n')
    f.write(final_content)

print('  ✅ Saved to: test_chunk_humanized_final.md')

# Save comparison
with open('test_chunk_comparison.md', 'w', encoding='utf-8') as f:
    f.write('# HUMANIZATION COMPARISON\n\n')
    f.write('## Original First 500 chars:\n\n')
    f.write(original_content[:500] + '...\n\n')
    f.write('## Humanized First 500 chars:\n\n')
    f.write(final_content[:500] + '...\n\n')
    f.write('## Statistics:\n\n')
    f.write(f'- Original: {original_words} words\n')
    f.write(f'- Humanized: {total_humanized_words} words\n')
    f.write(f'- Final: {final_words} words\n')
    f.write(f'- Accuracy: {(final_words/original_words)*100:.1f}%\n')

print('  ✅ Saved to: test_chunk_comparison.md')

# Final summary
print('\n' + '='*60)
print('FINAL SUMMARY:')
print(f'  Original: {original_words} words')
print(f'  After chunk humanization: {total_humanized_words} words')
print(f'  After expansion: {final_words} words')
print(f'  Target accuracy: {(final_words/original_words)*100:.1f}%')

if abs(final_words - original_words) <= 200:
    print('  ✅ SUCCESS: Within acceptable range!')
else:
    diff = final_words - original_words
    print(f'  ⚠️  Off by {diff:+d} words')

print('='*60)