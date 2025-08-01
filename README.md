# BMM SEO Agent

An intelligent keyword research tool powered by DataForSEO API and AI analysis through OpenRouter.

## Features

- 🔍 **Keyword Research**: Generate keyword suggestions using DataForSEO API
- 📊 **SERP Analysis**: Analyze search engine results pages
- 🤖 **AI Insights**: LLM-powered keyword analysis and content recommendations
- 📥 **Export Options**: CSV and Excel export functionality
- 🎯 **Advanced Filtering**: Filter by country, language, volume, and difficulty
- 📈 **Trend Analysis**: Historical search volume trends and Google Trends integration
- 📝 **Content Brief Generation**: AI-powered content briefs based on keyword and SERP data

## Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment Variables**
Create a `.env` file with your API credentials:
```bash
# DataForSEO API
DATAFORSEO_USERNAME=your_username
DATAFORSEO_PASSWORD=your_password
DATAFORSEO_API_KEY=your_api_key

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemini-2.0-flash-001
```

3. **Run the Application**
```bash
streamlit run app.py
```

## Project Structure

```
bmm-seo-agent/
├── app.py                 # Main Streamlit application
├── agents/
│   ├── __init__.py
│   └── keyword_agent.py   # Main keyword research agent
├── utils/
│   ├── __init__.py
│   ├── llm_client.py      # OpenRouter/LLM integration
│   └── export.py          # Export functionality
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not tracked)
└── README.md             # This file
```

## Usage

1. **Keyword Research**
   - Enter a seed keyword
   - Select country and language
   - Set volume and difficulty filters
   - Click "Generate Keywords"

2. **SERP Analysis**
   - Select a keyword from your research results
   - Click "Analyze SERP" to get top ranking pages
   - View AI-powered content gap analysis

3. **Export Data**
   - Use CSV or Excel export buttons
   - Data includes all filters and insights

## API Integration

### DataForSEO
- Uses official DataForSEO REST API
- Supports keyword suggestions and SERP analysis
- Includes fallback mock data for testing

### OpenRouter
- Supports multiple LLM models
- Provides AI insights and content recommendations
- Configurable model selection

## Development

### Adding New Features
1. Create new functions in appropriate modules
2. Update the Streamlit UI in `app.py`
3. Test with mock data first
4. Add proper error handling

### Testing
```bash
# Run with mock data (when APIs are unavailable)
python -c "from agents.keyword_agent import KeywordAgent; agent = KeywordAgent(); print(agent._generate_mock_keywords('seo tools', 100, 70))"
```

## Troubleshooting

### Common Issues
1. **API Authentication Errors**: Check your credentials in `.env`
2. **Rate Limiting**: DataForSEO has rate limits - space out requests
3. **Model Unavailable**: Try different OpenRouter models
4. **Export Issues**: Ensure proper pandas/openpyxl installation

### Error Handling
- All API calls include fallback mock data
- Export functions handle data formatting errors gracefully
- UI shows clear error messages for user actions

## Future Enhancements

- [x] Trend analysis with historical data (Available in Tab 4)
- [ ] Competitor keyword gap analysis
- [x] Content brief generation (Available in Tab 7)
- [ ] Keyword clustering visualization
- [ ] Batch keyword processing
- [ ] Custom model fine-tuning
- [ ] API rate limiting management
- [ ] User authentication and project management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is for internal use at Blue Moon Marketing.