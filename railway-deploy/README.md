# Bible Study API - Railway Deployment

This directory contains the Railway deployment configuration for the Bible Study API with full Gemini integration.

## Features

- ✅ Complete verse-by-verse study generation
- ✅ 28 thematic study rubriques 
- ✅ Google Gemini Flash integration for rich theological explanations
- ✅ Intelligent theological content system
- ✅ CORS properly configured for Vercel frontend

## Files

- `server.py` - Main FastAPI application with Gemini integration
- `requirements.txt` - Python dependencies including emergentintegrations
- `railway.toml` - Railway configuration
- `Procfile` - Process configuration for Railway
- `runtime.txt` - Python version specification
- `theological_*.py` - Intelligent content generation modules

## Deployment Instructions

### 1. Prerequisites
- Railway account with CLI installed
- Emergent LLM key for Gemini integration

### 2. Deploy to Railway

```bash
# Clone or prepare the railway-deploy directory
cd railway-deploy

# Initialize Railway project
railway login
railway init

# Set environment variables
railway variables set EMERGENT_LLM_KEY="your-emergent-llm-key-here"
railway variables set BIBLE_API_KEY="0cff5d83f6852c3044a180cc4cdeb0fe"
railway variables set BIBLE_ID="a93a92589195411f-01"

# Deploy
railway up
```

### 3. Configure Custom Domain (Optional)

```bash
# Add custom domain for etude8-bible-api-production.up.railway.app
railway domain add etude8-bible-api-production.up.railway.app
```

### 4. Verify Deployment

After deployment, verify endpoints:

- **Health Check**: `https://your-railway-url.up.railway.app/api/health`
- **Root**: `https://your-railway-url.up.railway.app/api/`
- **Verse Generation**: `POST https://your-railway-url.up.railway.app/api/generate-verse-by-verse`
- **Gemini Verse Generation**: `POST https://your-railway-url.up.railway.app/api/generate-verse-by-verse-gemini`
- **Study Generation**: `POST https://your-railway-url.up.railway.app/api/generate-study`

## Environment Variables Required

| Variable | Description | Default |
|----------|-------------|---------|
| `EMERGENT_LLM_KEY` | Emergent LLM key for Gemini integration | Required |
| `BIBLE_API_KEY` | API Bible key | `0cff5d83f6852c3044a180cc4cdeb0fe` |
| `BIBLE_ID` | Bible version ID (Darby FR) | `a93a92589195411f-01` |
| `PORT` | Railway port (auto-set) | `8000` |

## API Endpoints

### GET /api/health
Returns service status with Gemini availability

### POST /api/generate-verse-by-verse
Standard verse-by-verse generation

### POST /api/generate-verse-by-verse-gemini
Enhanced verse-by-verse with Gemini Flash

### POST /api/generate-study
Generates 28 thematic rubriques study

## Testing

```bash
# Test health endpoint
curl https://your-railway-url.up.railway.app/api/health

# Test verse generation with Gemini
curl -X POST https://your-railway-url.up.railway.app/api/generate-verse-by-verse-gemini \
  -H "Content-Type: application/json" \
  -d '{"passage": "Jean 3:16", "version": "LSG"}'
```

## Troubleshooting

1. **Cold Start Issues**: Railway services may have cold starts. First requests might take longer.

2. **Gemini Not Available**: Check if `EMERGENT_LLM_KEY` is properly set in Railway variables.

3. **CORS Issues**: Ensure frontend domain is added to ALLOWED_ORIGINS in server.py.

4. **Timeout Issues**: Gemini generation for large chapters may take 2-3 minutes.

## Version History

- **v2.0.0**: Added Gemini integration and intelligent theological system
- **v1.0.0**: Basic verse-by-verse and 28 rubriques generation