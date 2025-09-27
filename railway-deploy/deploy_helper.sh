#!/bin/bash
# Railway Deployment Helper Script

echo "🚀 Bible Study API - Railway Deployment Helper"
echo "=============================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI found"

# Login check
echo "📋 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "🔑 Please login to Railway:"
    railway login
fi

echo "✅ Railway authentication confirmed"

# Set environment variables
echo "⚙️  Setting environment variables..."

railway variables set EMERGENT_LLM_KEY="sk-emergent-3BcF2643421D02fC0E"
railway variables set BIBLE_API_KEY="0cff5d83f6852c3044a180cc4cdeb0fe"
railway variables set BIBLE_ID="a93a92589195411f-01"

echo "✅ Environment variables set"

# Deploy
echo "🚀 Starting deployment..."
railway up --detach

echo "✅ Deployment initiated"
echo ""
echo "📊 To monitor deployment:"
echo "   railway logs"
echo ""
echo "🔗 To get deployment URL:"
echo "   railway domain"
echo ""
echo "🧪 To test deployment:"
echo "   python test_deployment.py [your-railway-url]"