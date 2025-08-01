#!/bin/bash

echo "🔍 Starting BMM SEO Agent Demo..."
echo "====================================="

# Activate virtual environment
source venv/bin/activate

# Check if localtunnel is installed
if ! command -v lt &> /dev/null; then
    echo "📦 Installing localtunnel..."
    npm install -g localtunnel
fi

# Start Streamlit in background
echo "📊 Starting Streamlit app..."
streamlit run app.py --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# Wait for Streamlit to start
echo "⏳ Waiting for Streamlit to start..."
sleep 5

# Start LocalTunnel
echo "🌐 Creating public URL..."
echo "📝 Note: You may need to enter a password shown on the LocalTunnel page"
lt --port 8501 --print-requests

# When user stops the script, kill Streamlit too
trap "kill $STREAMLIT_PID" EXIT
wait