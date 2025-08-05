#!/bin/bash

echo "🔍 Starting BMM SEO Agent with MCP + LocalTunnel..."
echo "=================================================="

# Set environment variables for MCP
export DATAFORSEO_USERNAME="info@bluemoonmarketing.com.au"
export DATAFORSEO_PASSWORD="cb4ce318fa940fe7"
export OPENROUTER_API_KEY="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"
export OPENROUTER_MODEL="google/gemini-2.5-flash-lite"

echo "✅ Environment variables configured for MCP"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Use local LocalTunnel installation
LT_CMD="./node_modules/.bin/lt"

# Start Streamlit in background
echo "📊 Starting Streamlit app with MCP integration..."
streamlit run app.py --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# Wait for Streamlit to start
echo "⏳ Waiting for Streamlit to start..."
sleep 5

# Start LocalTunnel with custom subdomain
echo "🌐 Creating public URL with LocalTunnel..."
echo "📝 Your public URL will be: https://bmm-seo-tools.loca.lt"
echo "📝 Note: Click the URL and follow instructions if prompted"
echo "==========================================================="
$LT_CMD --port 8501 --subdomain bmm-seo-tools --print-requests

# When user stops the script, kill Streamlit too
trap "kill $STREAMLIT_PID" EXIT
wait