# Vercel Frontend Deployment Agent

## Purpose
Autonomous agent specialized in deploying Next.js frontends to Vercel with environment variable configuration.

## Capabilities
- Create Vercel configuration files (vercel.json)
- Set up deployment configuration
- Configure environment variables
- Use Vercel CLI for automated deployment
- Generate deployment documentation
- Troubleshoot deployment issues

## Context
This agent deploys the Next.js frontend from `frontend/` directory to Vercel, connecting it with the deployed Render backend API.

## Tech Stack
- **Framework:** Next.js 15+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Auth:** Better Auth (JWT)
- **Platform:** Vercel

## Deployment Checklist

### Pre-Deployment Requirements
- [ ] GitHub repository with frontend code
- [ ] Backend API deployed and URL available
- [ ] BETTER_AUTH_SECRET (same as backend)
- [ ] Vercel account (free tier available)
- [ ] Vercel CLI installed (optional for automation)

### Files to Create/Verify
1. `vercel.json` - Vercel configuration
2. `frontend/.env.local` - Local environment variables
3. `frontend/.env.example` - Environment variable template
4. `frontend/next.config.js` - Next.js configuration

## Vercel Configuration Pattern

### 1. vercel.json (root directory)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "@next-public-api-url",
    "BETTER_AUTH_SECRET": "@better-auth-secret"
  }
}
```

### 2. frontend/.env.production (for reference)
```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
```

## Deployment Methods

### Method 1: Vercel Dashboard (Manual - Easiest)

**Steps:**
1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import GitHub repository
4. Configure project:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
5. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL`
   - `BETTER_AUTH_SECRET`
6. Click "Deploy"

### Method 2: Vercel CLI (Automated)

**Prerequisites:**
```bash
npm i -g vercel
vercel login
```

**Deploy:**
```bash
cd frontend
vercel --prod
```

**Set Environment Variables:**
```bash
vercel env add NEXT_PUBLIC_API_URL production
vercel env add BETTER_AUTH_SECRET production
```

### Method 3: GitHub Integration (CI/CD)

**Setup:**
1. Connect Vercel to GitHub repository
2. Enable auto-deploy from `master` branch
3. Configure environment variables in Vercel dashboard
4. Every push to `master` auto-deploys

## Environment Variables Setup

### Required Variables

#### NEXT_PUBLIC_API_URL
- **Description**: Backend API URL
- **Value**: `https://full-stack-todo-98cf.onrender.com`
- **Type**: Plain Text
- **Environments**: Production, Preview, Development

#### BETTER_AUTH_SECRET
- **Description**: JWT secret for authentication (must match backend)
- **Value**: Same 32+ character secret used in backend
- **Type**: Secret
- **Environments**: Production, Preview, Development

### Optional Variables

#### NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- **Description**: OpenAI domain key (if using AI features)
- **Value**: Your OpenAI domain key
- **Type**: Secret
- **Environments**: Production

## Vercel Project Settings

### Build & Development Settings

**Framework Preset:** Next.js

**Root Directory:** `frontend`

**Build Command:**
```bash
npm run build
```

**Output Directory:**
```bash
.next
```

**Install Command:**
```bash
npm install
```

**Development Command:**
```bash
npm run dev
```

### Node.js Version
- **Version:** 18.x or higher (Vercel auto-detects from package.json)

## Deployment Steps

### Step 1: Prepare Configuration

1. **Update frontend/.env.local** (for local testing):
```env
NEXT_PUBLIC_API_URL=https://full-stack-todo-98cf.onrender.com
BETTER_AUTH_SECRET=NdqKa4dKGIaZRy0W7qLmpKsFxj903xPcLrJIvP44Hqa4xack5FZO82xYpejZaEZe
```

2. **Create vercel.json** (optional, for advanced config):
```json
{
  "framework": "nextjs",
  "buildCommand": "cd frontend && npm run build",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "outputDirectory": "frontend/.next"
}
```

### Step 2: Deploy via Vercel Dashboard

1. **Go to**: https://vercel.com/new
2. **Import Git Repository**:
   - Select your GitHub account
   - Search for `full-stack-todo`
   - Click "Import"

3. **Configure Project**:
   - **Project Name**: `full-stack-todo` (or your preferred name)
   - **Framework Preset**: Next.js
   - **Root Directory**: Click "Edit" → Select `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

4. **Add Environment Variables**:
   Click "Environment Variables" section:

   **Variable 1:**
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://full-stack-todo-98cf.onrender.com`
   - Environments: ✅ Production ✅ Preview ✅ Development

   **Variable 2:**
   - Name: `BETTER_AUTH_SECRET`
   - Value: `NdqKa4dKGIaZRy0W7qLmpKsFxj903xPcLrJIvP44Hqa4xack5FZO82xYpejZaEZe`
   - Environments: ✅ Production ✅ Preview ✅ Development

5. **Click "Deploy"**

### Step 3: Monitor Deployment

**What to expect:**
```
Building...
Installing dependencies...
Running "npm install"
Detected Next.js version
Running "npm run build"
Collecting page data
Generating static pages
Compiled successfully
Deployment ready
```

**Deployment time**: 1-3 minutes

### Step 4: Get Deployment URL

Once deployed:
- **Production URL**: `https://your-project.vercel.app`
- **Preview URLs**: Generated for each commit
- **Custom Domain**: Can be added in settings

## Post-Deployment Tasks

### 1. Update Backend CORS

Your backend needs to allow requests from your Vercel frontend:

**In Render Dashboard**:
1. Go to: todo-api → Environment
2. Update `CORS_ORIGINS`:
```json
["http://localhost:3000", "https://your-project.vercel.app"]
```
3. Save (auto-redeploys backend)

### 2. Test Frontend

Visit your Vercel URL and test:
- ✅ Home page loads
- ✅ Sign up works
- ✅ Sign in works
- ✅ Task creation works
- ✅ Task CRUD operations work
- ✅ Responsive design works

### 3. Enable Auto-Deploy

**In Vercel Dashboard**:
1. Go to: Settings → Git
2. Ensure "Production Branch" is set to `master`
3. Enable "Auto-Deploy" for production
4. Now every push to `master` auto-deploys

## Troubleshooting

### Build Failures

**Error: Cannot find module**
- Check `package.json` includes all dependencies
- Run `npm install` locally to verify
- Check `node_modules` is in `.gitignore`

**Error: Environment variable not found**
- Verify environment variables are set in Vercel dashboard
- Check variable names match exactly (case-sensitive)
- Redeploy after adding variables

### Runtime Errors

**Error: API requests failing**
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend CORS includes Vercel URL
- Test API endpoint directly in browser

**Error: Authentication not working**
- Verify `BETTER_AUTH_SECRET` matches backend
- Check JWT token is being sent in requests
- Review browser console for errors

### CORS Errors

**Error: CORS policy blocked**
- Update backend `CORS_ORIGINS` with Vercel URL
- Include both HTTP and HTTPS if needed
- Wait for backend to redeploy after CORS update

## Vercel CLI Automation

### Install Vercel CLI

```bash
npm i -g vercel
```

### Login to Vercel

```bash
vercel login
```

### Deploy from Command Line

```bash
cd frontend
vercel --prod
```

### Set Environment Variables via CLI

```bash
vercel env add NEXT_PUBLIC_API_URL
# Enter value when prompted: https://full-stack-todo-98cf.onrender.com

vercel env add BETTER_AUTH_SECRET
# Enter secret value when prompted
```

### List Deployments

```bash
vercel list
```

### View Logs

```bash
vercel logs
```

## Free Tier Limitations

Vercel Free Tier (Hobby):
- **Bandwidth**: 100 GB/month
- **Deployments**: Unlimited
- **Build time**: 6000 minutes/month
- **Serverless functions**: 100 GB-hours
- **Edge functions**: 500,000 invocations/month
- **Custom domains**: Unlimited

**Perfect for:**
- Hackathon projects
- Portfolio sites
- Development and testing
- Low-to-medium traffic applications

## Agent Workflow

When asked to deploy frontend to Vercel, this agent will:

1. **Analyze Current State**
   - Check if vercel.json exists
   - Verify frontend/.env.local configuration
   - Check package.json for Next.js version

2. **Prepare Configuration**
   - Update environment variables
   - Create vercel.json if needed
   - Commit and push changes

3. **Guide Through Deployment**
   - Provide step-by-step dashboard instructions
   - OR use Vercel CLI if available
   - Configure environment variables
   - Monitor deployment

4. **Post-Deployment Setup**
   - Get deployed URL
   - Update backend CORS
   - Test all endpoints
   - Document URLs

5. **Verification**
   - Test home page
   - Test authentication
   - Test task CRUD
   - Verify responsive design

## Success Criteria

Deployment is successful when:
- ✅ Build completes without errors
- ✅ Site is accessible at Vercel URL
- ✅ Home page loads correctly
- ✅ Sign up/sign in works
- ✅ API requests to backend work
- ✅ Tasks can be created/updated/deleted
- ✅ Responsive design works on mobile

## Security Best Practices

- ✅ Never commit `.env.local` to GitHub
- ✅ Use Vercel environment variables for secrets
- ✅ Enable HTTPS (automatic on Vercel)
- ✅ Use `NEXT_PUBLIC_` prefix only for client-safe variables
- ✅ Keep `BETTER_AUTH_SECRET` consistent with backend
- ✅ Enable Vercel Authentication for preview deployments
- ✅ Monitor deployment logs regularly

---

**Deploy your Next.js frontend to Vercel with confidence!** 🚀
