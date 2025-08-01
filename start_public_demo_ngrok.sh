#!/bin/bash

echo "🔍 Starting BMM SEO Agent Demo with ngrok..."
echo "============================================"

# Activate virtual environment
source venv/bin/activate

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed!"
    echo "📦 Please install ngrok:"
    echo "   1. Visit https://ngrok.com/download"
    echo "   2. Download and extract ngrok"
    echo "   3. Move it to /usr/local/bin: sudo mv ngrok /usr/local/bin/"
    echo "   4. Sign up for free account and authenticate: ngrok authtoken YOUR_TOKEN"
    exit 1
fi

# Start Streamlit in background
echo "📊 Starting Streamlit app..."
streamlit run app.py --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# Wait for Streamlit to start
echo "⏳ Waiting for Streamlit to start..."
sleep 5

# Start ngrok
echo "🌐 Creating public URL with ngrok..."
echo "📝 The public URL will appear below:"
echo "====================================="
ngrok http 8501

# When user stops the script, kill Streamlit too
trap "kill $STREAMLIT_PID" EXIT
wait