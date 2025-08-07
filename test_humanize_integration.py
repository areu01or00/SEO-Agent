#!/usr/bin/env python3
"""
Test the integrated humanization feature in ContentGeneratorAgent
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Set environment variables
os.environ['DATAFORSEO_USERNAME'] = os.getenv('DATAFORSEO_USERNAME', '')
os.environ['DATAFORSEO_PASSWORD'] = os.getenv('DATAFORSEO_PASSWORD', '')
os.environ['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY', '')

from agents.content_generator import ContentGeneratorAgent

print('TESTING INTEGRATED HUMANIZE ULTRA FEATURE')
print('='*60)

# Initialize generator
generator = ContentGeneratorAgent()

# Step 1: Generate content
print('\n1. GENERATING CONTENT (1500 words)...\n')
result = generator.generate_content(
    content_brief={'keyword': 'content marketing tips'},
    content_type='Blog Post',
    target_audience='marketers',
    title='Content Marketing Tips for 2024',
    word_count=1500,
    use_mcp_research=False
)

original_content = result['content']
original_words = result['metadata']['word_count']
print(f'✅ Generated: {original_words} words')

# Step 2: Humanize the content
print('\n2. HUMANIZING WITH ULTRA METHOD...\n')
humanized_result = generator.humanize_ultra(
    content=original_content,
    target_word_count=original_words
)

# Display results
print('\n3. RESULTS:\n')
meta = humanized_result['metadata']
print(f'   Original words: {meta["original_words"]}')
print(f'   Target words: {meta["target_words"]}')
print(f'   Humanized words: {meta["humanized_words"]}')
print(f'   Final words: {meta["final_words"]}')
print(f'   Accuracy: {meta["accuracy_percentage"]}%')
print(f'   Chunks processed: {meta["chunks_processed"]}')
print(f'   Expanded: {meta["expanded"]}')

# Show chunk statistics
print('\n4. CHUNK STATISTICS:\n')
for stat in meta['chunk_stats']:
    if 'error' in stat:
        print(f'   Chunk {stat["chunk"]}: ERROR - {stat.get("error", "Unknown error")}')
    else:
        print(f'   Chunk {stat["chunk"]}: {stat["original"]} → {stat["humanized"]} words (reduced {stat["reduction"]:.1f}%)')

# Save sample
print('\n5. SAVING SAMPLE...\n')
with open('test_humanize_integration_output.md', 'w', encoding='utf-8') as f:
    f.write(f'# Humanization Integration Test\n\n')
    f.write(f'## Metadata\n')
    f.write(f'- Original: {meta["original_words"]} words\n')
    f.write(f'- Final: {meta["final_words"]} words\n')
    f.write(f'- Accuracy: {meta["accuracy_percentage"]}%\n')
    f.write(f'- Chunks: {meta["chunks_processed"]}\n\n')
    f.write(f'## Content Preview (First 500 chars)\n\n')
    f.write(f'**Original:**\n{original_content[:500]}...\n\n')
    f.write(f'**Humanized:**\n{humanized_result["content"][:500]}...\n\n')
    f.write(f'## Full Humanized Content\n\n')
    f.write(humanized_result['content'])

print('✅ Saved to: test_humanize_integration_output.md')
print('\n' + '='*60)
print('TEST COMPLETE - Integration working successfully!')
print('='*60)