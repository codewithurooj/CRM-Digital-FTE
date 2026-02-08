# Dockerfile Generator Skill

## Purpose
Automatically generate optimized, production-ready Dockerfiles for various application frameworks. Creates multi-stage builds with best practices for security, performance, and minimal image sizes.

## Capabilities
- Generate multi-stage Dockerfiles for optimal layer caching
- Create framework-specific optimizations (Next.js, FastAPI, Python)
- Include health check endpoints
- Add security best practices (non-root user, minimal base images)
- Optimize for production (reduced image size, faster builds)
- Support environment variable configuration
- Include .dockerignore files

## Input Parameters
```typescript
{
  framework: 'nextjs' | 'fastapi' | 'python' | 'node';
  appDir: string;              // Application directory (e.g., "frontend", "backend")
  port: number;                // Exposed port (e.g., 3000, 8000)
  envVars?: string[];          // Required environment variables
  nodeVersion?: string;        // Node.js version (default: "20")
  pythonVersion?: string;      // Python version (default: "3.13")
}
```

## Output Structure

### Generated Files
```
{appDir}/
├── Dockerfile              # Multi-stage production Dockerfile
├── .dockerignore          # Exclude unnecessary files
└── docker-compose.yml     # Optional: for local testing
```

## Dockerfile Templates

### 1. Next.js Production Dockerfile

**File:** `frontend/Dockerfile`

**Features:**
- Multi-stage build (builder + runner)
- Standalone output for minimal size
- Layer caching optimization
- Non-root user for security
- Health check endpoint

```dockerfile
# ============================================
# Next.js Production Dockerfile
# Multi-stage build for optimized image size
# ============================================

# -------------------- Stage 1: Dependencies --------------------
FROM node:20-alpine AS deps
WORKDIR /app

# Install dependencies only when needed
# Copy package files first for better caching
COPY package.json package-lock.json* ./

# Install production dependencies
RUN npm ci --only=production && \
    # Cache production node_modules
    cp -R node_modules /tmp/node_modules && \
    # Install all dependencies for build
    npm ci

# -------------------- Stage 2: Builder --------------------
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build-time environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build Next.js application
# Automatically enables standalone output if configured
RUN npm run build

# -------------------- Stage 3: Runner --------------------
FROM node:20-alpine AS runner
WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Use non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set port environment variable
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["node", "server.js"]
```

**Required:** Update `next.config.js` to enable standalone output:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // ... other config
}

module.exports = nextConfig
```

---

### 2. FastAPI Production Dockerfile

**File:** `backend/Dockerfile`

**Features:**
- Python slim base for smaller image
- Multi-stage build
- Virtual environment
- Non-root user
- Health check
- Optimized layer caching

```dockerfile
# ============================================
# FastAPI Production Dockerfile
# Optimized for Python 3.13+ with uvicorn
# ============================================

# -------------------- Stage 1: Builder --------------------
FROM python:3.13-slim AS builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------- Stage 2: Runner --------------------
FROM python:3.13-slim AS runner
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1001 appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Use non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 3. Generic Python Application Dockerfile

**File:** `services/{service-name}/Dockerfile`

```dockerfile
# ============================================
# Python Application Dockerfile
# For microservices and workers
# ============================================

FROM python:3.13-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1001 appuser
USER appuser

# Run application
CMD ["python", "main.py"]
```

---

### 4. Node.js API Dockerfile

**File:** `backend/Dockerfile` (for Node.js backend)

```dockerfile
# ============================================
# Node.js API Dockerfile
# ============================================

FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

USER nodejs

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3001/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "dist/main.js"]
```

---

## .dockerignore Templates

### Next.js .dockerignore

**File:** `frontend/.dockerignore`

```
# Dependencies
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js build output
.next
out

# Testing
coverage
.nyc_output

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode
.idea
*.swp
*.swo

# Git
.git
.gitignore

# Documentation
README.md
docs

# Docker
Dockerfile
.dockerignore
docker-compose*.yml

# Misc
.DS_Store
*.log
```

### Python .dockerignore

**File:** `backend/.dockerignore`

```
# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache
.coverage
htmlcov/
.tox/

# Environment
.env
.env.local

# IDE
.vscode
.idea
*.swp

# Git
.git
.gitignore

# Documentation
README.md
docs/

# Docker
Dockerfile
.dockerignore
docker-compose*.yml

# Database
*.db
*.sqlite
```

---

## docker-compose.yml for Local Testing

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped

networks:
  default:
    name: todo-network
```

---

## Build Commands

### Build Images

```bash
# Frontend
docker build -t todo-frontend:latest ./frontend

# Backend
docker build -t todo-backend:latest ./backend

# With build args
docker build \
  --build-arg NODE_VERSION=20 \
  -t todo-frontend:latest \
  ./frontend
```

### Run Containers

```bash
# Frontend
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  todo-frontend:latest

# Backend
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e OPENAI_API_KEY=sk-... \
  todo-backend:latest

# With docker-compose
docker-compose up -d
```

### Test Images

```bash
# Check image size
docker images | grep todo

# Test health check
docker run -d --name test-frontend todo-frontend:latest
docker ps  # Check STATUS column for health
docker logs test-frontend

# Clean up
docker stop test-frontend
docker rm test-frontend
```

---

## Optimization Best Practices

### 1. **Layer Caching**
Copy dependency files first, then application code:
```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
COPY . .  # Only re-runs if app code changes
```

### 2. **Multi-Stage Builds**
Separate build dependencies from runtime:
- Builder stage: includes dev dependencies, build tools
- Runner stage: only production dependencies and built artifacts

### 3. **Minimal Base Images**
- Use `alpine` variants when possible
- Use `slim` for Python
- Reduces image size by 50-70%

### 4. **Security**
```dockerfile
# Non-root user
RUN useradd -m -u 1001 appuser
USER appuser

# Scan for vulnerabilities
docker scan todo-frontend:latest
```

### 5. **Health Checks**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

---

## Image Size Comparisons

| Framework | Without Optimization | Optimized | Savings |
|-----------|---------------------|-----------|---------|
| Next.js | ~1.2 GB | ~180 MB | 85% |
| FastAPI | ~900 MB | ~150 MB | 83% |
| Python App | ~800 MB | ~120 MB | 85% |

---

## Usage Examples

### Example 1: Generate Next.js Dockerfile

```bash
# User command
"Use dockerfile-generator to create Next.js production Dockerfile for frontend"

# Claude generates:
✅ frontend/Dockerfile (multi-stage, optimized)
✅ frontend/.dockerignore
✅ Updated frontend/next.config.js (standalone output)

# Ready to build:
cd frontend
docker build -t todo-frontend:latest .
```

### Example 2: Generate FastAPI Dockerfile

```bash
# User command
"Use dockerfile-generator to create FastAPI Dockerfile for backend on port 8000"

# Claude generates:
✅ backend/Dockerfile (Python 3.13, uvicorn)
✅ backend/.dockerignore
✅ backend/docker-compose.yml (optional)

# Ready to build:
cd backend
docker build -t todo-backend:latest .
```

### Example 3: Generate with Custom Configuration

```bash
# User command
"Create Dockerfile for backend with Python 3.12 and port 9000"

# Claude generates:
✅ Custom Dockerfile with Python 3.12
✅ Exposed port 9000
✅ Health check on /health endpoint
```

---

## Integration with Kubernetes

Generated Dockerfiles are optimized for Kubernetes deployment:

### 1. **Health Checks**
Map to Kubernetes probes:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 40
  periodSeconds: 30
```

### 2. **Non-root User**
Meets Kubernetes security requirements:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
```

### 3. **Resource Efficiency**
Small images = faster pod startup:
- Optimized Next.js: ~180 MB
- Optimized FastAPI: ~150 MB

---

## Troubleshooting

### Issue: Image build fails

**Solution:**
```bash
# Check Docker version
docker --version

# Build with verbose output
docker build --progress=plain -t app:latest .

# Clear build cache
docker builder prune
```

### Issue: Health check fails

**Solution:**
```bash
# Test health endpoint locally
docker run -p 8000:8000 app:latest
curl http://localhost:8000/health

# Check logs
docker logs <container-id>
```

### Issue: Image too large

**Solution:**
- Use multi-stage builds
- Use alpine/slim base images
- Add more to .dockerignore
- Remove dev dependencies

---

## Time Savings

**Manual Dockerfile Creation:**
- Research best practices: 30 minutes
- Write Dockerfile: 30 minutes
- Debug issues: 1 hour
- Optimize: 30 minutes
- **Total: 2-3 hours per application**

**With This Skill:**
- Generation: 1 minute
- Review: 5 minutes
- **Total: 5-10 minutes per application**

**Time Saved: 95%** ⚡

---

## Quality Benefits

✅ **Production-Ready** - Multi-stage builds, optimized layers
✅ **Secure** - Non-root users, minimal attack surface
✅ **Efficient** - 80%+ smaller image sizes
✅ **Reliable** - Health checks, proper logging
✅ **Consistent** - Same patterns across all services

---

## Reusability

Use this skill for:
- **Phase 4:** Docker containerization
- **Phase 5:** Microservices (recurring, notification)
- **Future Projects:** Any Node.js or Python app
- **Production Deployments:** Ready for cloud

---

## Success Metrics

Generated Dockerfiles should:
- ✅ Build successfully without errors
- ✅ Images < 200 MB for production apps
- ✅ Health checks pass
- ✅ Run as non-root user
- ✅ Start in < 30 seconds
- ✅ Pass security scans

---

**This skill generates production-ready Dockerfiles in seconds!** 🐳
