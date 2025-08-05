#!/bin/bash

# Start script for Railway deployment
echo "🚀 Starting BMM SEO Agent..."

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Start Streamlit application
echo "🌟 Starting Streamlit application..."
streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0