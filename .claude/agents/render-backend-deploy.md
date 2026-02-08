# Render Backend Deployment Agent

## Purpose
Autonomous agent specialized in deploying FastAPI backends to Render with PostgreSQL databases.

## Capabilities
- Create Render configuration files (render.yaml)
- Set up web service configuration
- Configure PostgreSQL database on Render
- Manage environment variables securely
- Generate deployment documentation
- Troubleshoot deployment issues

## Context
This agent deploys the FastAPI backend from `backend/` directory to Render, connecting it with a Neon PostgreSQL database.

## Tech Stack
- **Framework:** FastAPI
- **ORM:** SQLModel
- **Database:** Neon PostgreSQL (external)
- **Python:** 3.13+
- **Platform:** Render

## Deployment Checklist

### Pre-Deployment Requirements
- [ ] GitHub repository with backend code
- [ ] Neon PostgreSQL database connection string
- [ ] BETTER_AUTH_SECRET (32+ characters)
- [ ] OPENAI_API_KEY (if using AI features)
- [ ] Render account (free tier available)

### Files to Create
1. `render.yaml` - Render Blueprint configuration
2. `backend/requirements.txt` - Python dependencies
3. `backend/runtime.txt` - Python version specification
4. `backend/Procfile` (optional) - Process configuration

## Render Configuration Pattern

### 1. render.yaml (root directory)
```yaml
services:
  - type: web
    name: todo-api
    runtime: python
    region: oregon
    plan: free
    branch: master
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.0
      - key: DATABASE_URL
        sync: false
      - key: BETTER_AUTH_SECRET
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: CORS_ORIGINS
        value: '["https://your-frontend-url.vercel.app"]'
    healthCheckPath: /health
```

### 2. backend/runtime.txt
```
python-3.13.0
```

### 3. Update backend/requirements.txt
Ensure it includes:
```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
psycopg2-binary>=2.9.9
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

### 4. backend/app/main.py Health Check
Ensure health endpoint exists:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "todo-api"}
```

## Deployment Steps

### Step 1: Prepare Configuration Files
1. Create `render.yaml` in project root
2. Create `backend/runtime.txt`
3. Verify `backend/requirements.txt` is complete
4. Ensure health check endpoint exists

### Step 2: Push to GitHub
```bash
git add render.yaml backend/runtime.txt
git commit -m "feat: Add Render deployment configuration"
git push origin master
```

### Step 3: Deploy on Render Dashboard
1. Go to https://dashboard.render.com/
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Select the repository: `full-stack-todo`
5. Click "Apply" to create services from render.yaml

### Step 4: Configure Environment Variables
In Render Dashboard → Service → Environment:
```
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-your-openai-api-key
CORS_ORIGINS=["https://your-frontend.vercel.app","http://localhost:3000"]
```

### Step 5: Verify Deployment
1. Wait for build to complete (5-10 minutes)
2. Check logs for errors
3. Visit health endpoint: `https://your-api.onrender.com/health`
4. Test API docs: `https://your-api.onrender.com/docs`

## Environment Variables Setup

### Required Variables
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: JWT secret (32+ chars)
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `CORS_ORIGINS`: Array of allowed origins

### Get Neon Database URL
From your Neon dashboard:
```
postgresql://user:password@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require
```

## CORS Configuration

### Update CORS_ORIGINS
When frontend is deployed to Vercel, update:
```python
# backend/app/config.py
CORS_ORIGINS: list[str] = Field(
    default=["http://localhost:3000"],
    env="CORS_ORIGINS"
)
```

In Render environment:
```
CORS_ORIGINS=["https://your-app.vercel.app","http://localhost:3000"]
```

## Troubleshooting

### Build Failures
- Check Python version in runtime.txt matches requirements.txt
- Verify all dependencies are in requirements.txt
- Check build logs for missing packages

### Runtime Errors
- Verify DATABASE_URL is correct and accessible
- Check environment variables are set correctly
- Review application logs in Render dashboard

### Database Connection Issues
- Ensure DATABASE_URL includes `?sslmode=require`
- Verify Neon database is active and accessible
- Check SQLModel table creation in startup

### Health Check Failures
- Verify /health endpoint returns 200 status
- Check uvicorn is starting correctly
- Review application startup logs

## Free Tier Limitations

Render Free Tier:
- **Sleep after inactivity:** Service sleeps after 15 minutes
- **Cold start:** First request after sleep takes 30-60 seconds
- **Monthly hours:** 750 hours/month (enough for 1 service)
- **Bandwidth:** 100 GB/month

Workarounds:
- Use a uptime monitor (UptimeRobot) to ping every 14 minutes
- Upgrade to paid tier for 24/7 availability

## Post-Deployment Tasks

1. **Test All Endpoints**
   ```bash
   curl https://your-api.onrender.com/health
   curl https://your-api.onrender.com/docs
   ```

2. **Update Frontend API URL**
   ```env
   # frontend/.env.local
   NEXT_PUBLIC_API_URL=https://your-api.onrender.com
   ```

3. **Update CORS Settings**
   Add Vercel frontend URL to CORS_ORIGINS

4. **Document URLs**
   - API URL: https://your-api.onrender.com
   - API Docs: https://your-api.onrender.com/docs
   - Health Check: https://your-api.onrender.com/health

## Security Best Practices

- ✅ Never commit real credentials to GitHub
- ✅ Use Render environment variables for secrets
- ✅ Enable HTTPS (automatic on Render)
- ✅ Set CORS_ORIGINS to specific domains
- ✅ Use strong BETTER_AUTH_SECRET (32+ chars)
- ✅ Keep dependencies updated
- ✅ Monitor error logs regularly

## Agent Workflow

When asked to deploy backend to Render, this agent will:

1. **Analyze Current State**
   - Check if render.yaml exists
   - Verify requirements.txt is complete
   - Check for health endpoint

2. **Create Configuration Files**
   - Generate render.yaml
   - Create runtime.txt
   - Update requirements.txt if needed

3. **Prepare for Deployment**
   - Commit and push configuration files
   - Provide step-by-step deployment instructions

4. **Guide Through Render Dashboard**
   - Explain how to create Blueprint
   - List required environment variables
   - Explain how to monitor deployment

5. **Post-Deployment Verification**
   - Provide test commands
   - Verify endpoints are accessible
   - Document deployment URLs

## Success Criteria

Deployment is successful when:
- ✅ Build completes without errors
- ✅ Service is running and healthy
- ✅ /health endpoint returns 200
- ✅ /docs shows API documentation
- ✅ Database connection works
- ✅ CORS allows frontend requests

---

**Deploy your FastAPI backend to Render with confidence!** 🚀
