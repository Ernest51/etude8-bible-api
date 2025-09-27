# Migration Guide: Updating Railway API with Gemini

## Overview

This guide will help you update the existing `etude8-bible-api-production.up.railway.app` to include Gemini integration and rich theological explanations.

## Current Issue

The deployed Railway API only provides basic explanations:
```
"Ce récit des origines éclaire un aspect fondamental de la relation entre Dieu, l'humanité et la création."
```

## Solution

Deploy the enhanced version with Gemini integration that provides rich, contextual explanations for each verse.

## Quick Migration Steps

### 1. Backup Current Deployment
Before making changes, note your current Railway project details.

### 2. Deploy Enhanced Version

**Option A: Update Existing Railway Project**
```bash
# Connect to your existing Railway project
railway login
railway link [your-project-id]

# Update environment variables
railway variables set EMERGENT_LLM_KEY="your-key-here"

# Deploy new code
# Upload all files from railway-deploy/ directory to your Railway project
railway up
```

**Option B: Create New Railway Project**
```bash
railway login
railway init
railway variables set EMERGENT_LLM_KEY="your-key-here" 
railway variables set BIBLE_API_KEY="0cff5d83f6852c3044a180cc4cdeb0fe"
railway up
```

### 3. Update Domain (if needed)
Ensure your custom domain points to the new deployment:
- `etude8-bible-api-production.up.railway.app`

### 4. Test the Migration
```bash
python test_deployment.py https://etude8-bible-api-production.up.railway.app
```

### 5. Verify Frontend Integration
Test on https://etude8-bible.vercel.app/:
- ✅ Gemini button should now work
- ✅ Rich explanations should appear for each verse
- ✅ No more "Ce récit des origines..." repetition

## Expected Results After Migration

### Before (Current Railway API)
```json
{
  "content": "**EXPLICATION THÉOLOGIQUE :**\nCe récit des origines éclaire un aspect fondamental de la relation entre Dieu, l'humanité et la création."
}
```

### After (Enhanced Railway API with Gemini)
```json
{
  "content": "**EXPLICATION THÉOLOGIQUE :**\nDans Genèse 15:1, l'intervention divine auprès d'Abram survient \"après ces choses,\" vraisemblablement après sa victoire militaire rapportée au chapitre 14. Cette victoire, bien que significative, a pu laisser Abram vulnérable et craintif face à d'éventuelles représailles..."
}
```

## New Endpoints Available

After migration, these endpoints will be available:

- `GET /api/health` - Enhanced health check with Gemini status
- `POST /api/generate-verse-by-verse` - Standard generation 
- `POST /api/generate-verse-by-verse-gemini` - Enhanced with Gemini Flash
- `POST /api/generate-study` - 28 rubriques generation

## Troubleshooting

**Issue**: Gemini not working after deployment
**Solution**: Check if `EMERGENT_LLM_KEY` is set correctly in Railway variables

**Issue**: Cold start timeouts
**Solution**: First request may take 30-60 seconds for Railway to wake up

**Issue**: CORS errors
**Solution**: Verify `https://etude8-bible.vercel.app` is in ALLOWED_ORIGINS

## Rollback Plan

If issues occur, you can quickly rollback:
1. Redeploy the previous version
2. Or temporarily redirect traffic to the working `etude28-bible-api-production`

## Support

For issues during migration, check:
1. Railway deployment logs
2. Test script output
3. Frontend console errors on Vercel