# Railway Deployment Guide

## Free Hosting + Custom Domain + MCP Support

This guide will deploy your BMM SEO Agent to Railway with:
- ✅ Free hosting (500 execution hours/month)
- ✅ Custom domain support (`seo.bluemoonmarketing.com.au`)
- ✅ Node.js 20+ with MCP integration
- ✅ Real DataForSEO data

## Step 1: Push to GitHub

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit: BMM SEO Agent with MCP"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/bmm-seo-agent.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Railway

1. **Sign up at Railway**: https://railway.app
2. **Connect GitHub**: Link your GitHub account
3. **Deploy from GitHub**: Select your `bmm-seo-agent` repository
4. **Railway will automatically detect**:
   - `nixpacks.toml` (Node.js 20 + Python 3.12)
   - `Procfile` (Streamlit startup command)
   - `package.json` (DataForSEO MCP server)

## Step 3: Set Environment Variables

In Railway dashboard → Variables:

```
DATAFORSEO_USERNAME=info@bluemoonmarketing.com.au
DATAFORSEO_PASSWORD=cb4ce318fa940fe7
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=google/gemini-2.5-flash-lite
```

## Step 4: Custom Domain Setup

### In Railway:
1. Go to Settings → Networking
2. Add custom domain: `seo.bluemoonmarketing.com.au`
3. Railway provides DNS instructions

### In Cloudflare (your domain DNS):
1. Add CNAME record:
   - Name: `seo`
   - Target: `your-app-name.up.railway.app`
2. Set SSL/TLS to "Full"

## Step 5: Verify Deployment

Your app will be available at:
- Railway URL: `https://your-app-name.up.railway.app`
- Custom domain: `https://seo.bluemoonmarketing.com.au`

## Architecture on Railway

```
Railway Cloud Environment
├── Node.js 20.x (MCP server support)
├── Python 3.12 (Streamlit + agents)
├── Global dataforseo-mcp-server installation
├── Environment variables (credentials)
└── Custom domain with SSL
```

## Expected Features

- ✅ All 8 tabs working with real DataForSEO data
- ✅ MCP subprocess communication
- ✅ AI-powered insights via OpenRouter
- ✅ Professional URL on your domain
- ✅ Automatic HTTPS certificate
- ✅ Zero hosting costs (free tier)

## Monitoring

Railway provides:
- Real-time logs
- Deployment status
- Resource usage
- Custom domain SSL status

## Alternative: Render Deployment

If Railway doesn't work, Render also supports:
- Node.js + Python
- Custom domains
- Free tier
- MCP integration