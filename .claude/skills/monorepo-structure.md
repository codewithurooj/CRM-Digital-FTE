# Monorepo Structure Skill

## Purpose
Automatically generate a complete, production-ready monorepo structure for full-stack Phase 2 projects following Spec-Kit Plus conventions and hackathon requirements.

## Capabilities
- Create organized folder structure for frontend, backend, and specs
- Generate all configuration files (package.json, requirements.txt, etc.)
- Set up CLAUDE.md files at root, frontend, and backend levels
- Create docker-compose.yml for local development
- Initialize Spec-Kit Plus directory structure
- Generate .gitignore files
- Create comprehensive README.md
- Set up environment variable templates

## Input Parameters
```typescript
{
  projectName: string;           // e.g., "todo-app"
  phase: 'phase2' | 'phase3' | 'phase4' | 'phase5';
  description: string;           // Project description
  author?: string;               // Your name
}
```

## Complete Structure

### Generated Directory Tree
```
project-root/
├── .specify/                           # Spec-Kit Plus configuration
│   ├── memory/
│   │   └── constitution.md             # Project principles
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── adr-template.md
│   │   └── phr-template.prompt.md
│   └── scripts/
│       └── bash/
│           ├── create-adr.sh
│           ├── create-phr.sh
│           └── common.sh
│
├── specs/                              # All specifications
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   │   ├── task-crud.md
│   │   ├── authentication.md
│   │   └── .gitkeep
│   ├── api/
│   │   ├── rest-endpoints.md
│   │   └── .gitkeep
│   ├── database/
│   │   ├── schema.md
│   │   └── .gitkeep
│   └── ui/
│       ├── components.md
│       ├── pages.md
│       └── .gitkeep
│
├── history/                            # Historical records
│   ├── prompts/
│   │   ├── constitution/
│   │   ├── general/
│   │   └── .gitkeep
│   └── adr/
│       └── .gitkeep
│
├── frontend/                           # Next.js application
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── tasks/
│   │   │   └── page.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   │   └── .gitkeep
│   │   └── .gitkeep
│   ├── lib/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── utils.ts
│   ├── public/
│   │   └── .gitkeep
│   ├── .env.local.example
│   ├── .gitignore
│   ├── CLAUDE.md
│   ├── next.config.js
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── README.md
│
├── backend/                            # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── routes/
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── auth.py
│   │   └── utils/
│   │       └── __init__.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── conftest.py
│   ├── .env.example
│   ├── .gitignore
│   ├── CLAUDE.md
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── README.md
│
├── .claude/                            # Claude Code config
│   ├── commands/
│   │   └── .gitkeep
│   └── skills/
│       ├── spec-writer.md
│       ├── fastapi-sqlmodel.md
│       └── monorepo-structure.md
│
├── .gitignore
├── CLAUDE.md
├── README.md
├── docker-compose.yml
└── .env.example
```

## Generated Files Content

### 1. Root CLAUDE.md
```markdown
# {ProjectName} - Hackathon II Phase 2

## Project Overview
A full-stack todo application built using spec-driven development with Claude Code and Spec-Kit Plus.

**Phase:** Phase 2 - Full-Stack Web Application
**Due Date:** December 14, 2025
**Points:** 150

## Technology Stack

### Frontend
- **Framework:** Next.js 16+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Auth:** Better Auth (JWT)
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.13+
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Deployment:** Render/Railway

### Development Tools
- **Spec-Driven:** Claude Code + Spec-Kit Plus
- **Containerization:** Docker Compose
- **Version Control:** Git + GitHub

## Project Structure

```
├── frontend/       # Next.js 16+ application
├── backend/        # FastAPI server
├── specs/          # Feature specifications
├── history/        # PHRs and ADRs
└── .claude/        # Claude Code configuration
```

## Spec-Kit Plus Organization

### Specifications Directory (`/specs`)
- **`/specs/features/`** - What to build (user stories, requirements)
- **`/specs/api/`** - API contracts and endpoints
- **`/specs/database/`** - Schema and data models
- **`/specs/ui/`** - UI components and pages

### History Directory (`/history`)
- **`/history/prompts/`** - Prompt History Records (PHRs)
- **`/history/adr/`** - Architecture Decision Records

## Development Workflow

### Spec-Driven Development Process
1. **Write Specification**
   ```bash
   # Use spec-writer skill
   "Use spec-writer skill to create task CRUD spec"
   ```

2. **Generate Backend Code**
   ```bash
   # Use fastapi-sqlmodel skill
   "Use fastapi-sqlmodel skill to create Task API from @specs/features/task-crud.md"
   ```

3. **Generate Frontend Code**
   ```bash
   # Use nextjs-auth skill
   "Use nextjs-auth skill to create Task UI from @specs/ui/task-management.md"
   ```

4. **Test Implementation**
   ```bash
   # Backend tests
   cd backend && pytest

   # Frontend tests
   cd frontend && npm test
   ```

5. **Create PHR**
   ```bash
   # Document your work
   /sp.phr
   ```

## Quick Start Commands

### Development Servers

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# Runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

**Both (Docker):**
```bash
docker-compose up
```

### Testing

**Backend:**
```bash
cd backend
pytest                    # Run all tests
pytest --cov             # With coverage
pytest -v                # Verbose output
```

**Frontend:**
```bash
cd frontend
npm test                 # Run tests
npm run test:watch      # Watch mode
```

## Environment Setup

### Required Environment Variables

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-openai-domain-key
```

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-your-openai-api-key
```

## Claude Code Skills

Available skills in `.claude/skills/`:

### 1. Spec-Writer
Generates comprehensive specifications from natural language.
```bash
"Use spec-writer skill to create [feature] specification"
```

### 2. FastAPI + SQLModel
Generates complete backend with models, routes, and tests.
```bash
"Use fastapi-sqlmodel skill to create [Resource] API"
```

### 3. Next.js + Better Auth
Generates frontend components with authentication.
```bash
"Use nextjs-auth skill to create [Component] UI"
```

## Slash Commands

- `/sp.specify` - Create/update feature specification
- `/sp.plan` - Generate implementation plan
- `/sp.tasks` - Generate task list
- `/sp.implement` - Execute implementation
- `/sp.phr` - Record prompt history
- `/sp.adr` - Create architecture decision record

## Phase 2 Requirements

### Features to Implement
- ✅ Task CRUD operations (Create, Read, Update, Delete)
- ✅ User authentication (signup/signin)
- ✅ JWT-based API security
- ✅ Responsive UI with Tailwind CSS
- ✅ PostgreSQL database with Neon

### API Endpoints Required
```
GET    /api/{user_id}/tasks          # List all tasks
POST   /api/{user_id}/tasks          # Create task
GET    /api/{user_id}/tasks/{id}     # Get task
PUT    /api/{user_id}/tasks/{id}     # Update task
DELETE /api/{user_id}/tasks/{id}     # Delete task
PATCH  /api/{user_id}/tasks/{id}/complete  # Toggle completion
```

### Submission Requirements
1. ✅ Public GitHub repository
2. ✅ Deployed frontend (Vercel)
3. ✅ Deployed backend (Render/Railway)
4. ✅ Demo video (< 90 seconds)
5. ✅ All specs in `/specs` directory
6. ✅ PHRs in `/history/prompts`

## Helpful References

- **Hackathon PDF:** `Hackathon II - Todo Spec-Driven Development.pdf`
- **Frontend Patterns:** `frontend/CLAUDE.md`
- **Backend Patterns:** `backend/CLAUDE.md`
- **Spec Examples:** `/specs/features/`

## Getting Help

### Read Relevant Specs First
```bash
# Before implementing, read:
@specs/features/[feature].md
@specs/api/rest-endpoints.md
@specs/database/schema.md
```

### Reference Code Patterns
```bash
# Frontend patterns
@frontend/CLAUDE.md

# Backend patterns
@backend/CLAUDE.md
```

### Use Skills
```bash
# Generate code quickly
"Use [skill-name] skill to [action]"
```

## Success Metrics

- ✅ All 5 basic CRUD features working
- ✅ User authentication functional
- ✅ All tests passing (90%+ coverage)
- ✅ Deployed and accessible online
- ✅ Demo video submitted
- ✅ Specs and PHRs documented

## Next Steps

1. **Set up environment variables** (see above)
2. **Create task CRUD specification** using spec-writer skill
3. **Generate backend** using fastapi-sqlmodel skill
4. **Generate frontend** using nextjs-auth skill
5. **Test locally**
6. **Deploy to Vercel + Render**
7. **Record demo video**
8. **Submit by December 14, 2025**

---

**Let's build this with spec-driven development!** 🚀
```

### 2. Frontend CLAUDE.md
```markdown
# Frontend Development Guidelines

## Stack
- **Framework:** Next.js 16+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Authentication:** Better Auth (JWT)

## Project Structure
```
frontend/
├── app/              # Pages and layouts (App Router)
│   ├── (auth)/      # Auth group routes
│   ├── tasks/       # Task pages
│   ├── layout.tsx   # Root layout
│   └── page.tsx     # Home page
├── components/       # Reusable components
│   └── ui/          # Base UI components
├── lib/             # Utilities
│   ├── api.ts       # API client
│   ├── auth.ts      # Auth helpers
│   └── utils.ts     # Utility functions
└── public/          # Static assets
```

## Development Patterns

### Server vs Client Components
```tsx
// Server Component (default)
// app/tasks/page.tsx
export default async function TasksPage() {
  // Can fetch data directly
  const tasks = await getTasks()
  return <TaskList tasks={tasks} />
}

// Client Component (interactive)
// components/TaskItem.tsx
'use client'

import { useState } from 'react'

export function TaskItem() {
  const [isEditing, setIsEditing] = useState(false)
  // Interactive features here
}
```

### API Client Usage
All backend calls through `/lib/api.ts`:

```typescript
import { api } from '@/lib/api'

// In Server Component
const tasks = await api.getTasks()

// In Client Component
const handleCreate = async () => {
  const task = await api.createTask({
    title: 'New task',
    description: 'Description'
  })
}
```

### Authentication
Better Auth with JWT stored in httpOnly cookies:

```typescript
// Check auth status
import { auth } from '@/lib/auth'

const session = await auth.getSession()

// Protect routes
if (!session) {
  redirect('/login')
}

// Get user ID
const userId = session.user.id
```

### Styling with Tailwind
```tsx
// Use Tailwind classes
<div className="flex items-center gap-4 p-4 rounded-lg border">
  <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Save
  </button>
</div>

// Responsive design
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content */}
</div>
```

### Error Handling
```tsx
// Use error boundaries
// app/error.tsx
'use client'

export default function Error({ error, reset }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}

// Loading states
// app/loading.tsx
export default function Loading() {
  return <div>Loading...</div>
}
```

## Common Patterns

### Form Handling
```tsx
'use client'

export function TaskForm() {
  const [formData, setFormData] = useState({ title: '', description: '' })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.createTask(formData)
      // Success handling
    } catch (error) {
      // Error handling
    }
  }

  return <form onSubmit={handleSubmit}>{/* Form fields */}</form>
}
```

### Data Fetching
```tsx
// Server Component - Direct fetch
export default async function Page() {
  const data = await fetch('...').then(r => r.json())
  return <Component data={data} />
}

// Client Component - Use SWR or React Query
'use client'
import useSWR from 'swr'

export function Component() {
  const { data, error, isLoading } = useSWR('/api/tasks', fetcher)
  if (isLoading) return <Loading />
  if (error) return <Error />
  return <TaskList tasks={data} />
}
```

## TypeScript Types
```typescript
// Define types in lib/types.ts
export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  completed?: boolean
}
```

## Running & Building

```bash
# Development
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Production build
npm run build

# Start production server
npm run start
```

## Environment Variables
Required in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-32-chars-min
```

## Best Practices
- ✅ Use Server Components by default
- ✅ Add 'use client' only when needed
- ✅ Keep components small and focused
- ✅ Use TypeScript for all files
- ✅ Follow Tailwind CSS conventions
- ✅ Handle loading and error states
- ✅ Implement proper error boundaries
- ✅ Use the API client for all requests
- ✅ Never expose secrets in client code

---

**Build fast, type-safe React apps with Next.js!** ⚛️
```

### 3. Backend CLAUDE.md
```markdown
# Backend Development Guidelines

## Stack
- **Framework:** FastAPI
- **Language:** Python 3.13+
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL

## Project Structure
```
backend/
├── app/
│   ├── main.py          # FastAPI app entry
│   ├── config.py        # Configuration
│   ├── database.py      # DB connection
│   ├── models/          # SQLModel models
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   ├── middleware/      # Middleware (auth, etc.)
│   └── utils/           # Utility functions
└── tests/               # Pytest tests
```

## Development Patterns

### FastAPI Routes
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

@router.get("/")
async def list_tasks(
    user_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    # Verify authorization
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Query database
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks
```

### SQLModel Models
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Database Sessions
```python
from sqlmodel import Session, create_engine

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
```

### Authentication Middleware
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

def get_current_user_id(credentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub") or payload.get("user_id")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## API Conventions

### RESTful Endpoints
```
GET    /api/{user_id}/tasks          # List all
POST   /api/{user_id}/tasks          # Create
GET    /api/{user_id}/tasks/{id}     # Get one
PUT    /api/{user_id}/tasks/{id}     # Update
DELETE /api/{user_id}/tasks/{id}     # Delete
PATCH  /api/{user_id}/tasks/{id}/complete  # Custom action
```

### Response Formats
```python
# Success (200 OK)
{
  "id": 1,
  "title": "Task",
  "completed": false,
  ...
}

# Error (400/401/403/404/500)
{
  "detail": "Error message"
}
```

### HTTP Status Codes
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing/invalid auth
- `403 Forbidden` - Valid auth, no permission
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server error

## Testing with Pytest

```python
import pytest
from fastapi.testclient import TestClient

def test_create_task(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/test-user/tasks/",
        json={"title": "Test", "description": "Description"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
```

## Running & Testing

```bash
# Development server
uvicorn app.main:app --reload

# Run all tests
pytest

# With coverage
pytest --cov

# Verbose output
pytest -v

# Run specific test
pytest tests/test_tasks.py::test_create_task
```

## Environment Variables
Required in `.env`:
```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname
BETTER_AUTH_SECRET=your-secret-32-chars-min
OPENAI_API_KEY=sk-your-key
```

## Best Practices
- ✅ Always verify user_id matches authenticated user
- ✅ Use SQLModel for all database operations
- ✅ Include comprehensive error handling
- ✅ Write tests for all endpoints
- ✅ Use Pydantic for validation
- ✅ Return proper HTTP status codes
- ✅ Add API documentation (auto-generated)
- ✅ Use async/await for I/O operations
- ✅ Filter all queries by user_id
- ✅ Never expose sensitive data

---

**Build secure, scalable APIs with FastAPI!** 🚀
```

### 4. docker-compose.yml
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    command: npm run dev

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

networks:
  default:
    name: todo-network
```

### 5. Root README.md
```markdown
# {ProjectName}

> Hackathon II: The Evolution of Todo - Full-Stack Application with Spec-Driven Development

## 🎯 Project Overview

A modern todo application built using spec-driven development with Claude Code and Spec-Kit Plus for Hackathon II Phase 2.

**Phase:** Phase 2 - Full-Stack Web Application
**Due:** December 14, 2025
**Points:** 150

## ✨ Features

- ✅ Task CRUD operations (Create, Read, Update, Delete)
- ✅ User authentication with Better Auth
- ✅ JWT-based API security
- ✅ Responsive UI with Tailwind CSS
- ✅ Real-time updates
- ✅ PostgreSQL database with Neon

## 🛠️ Tech Stack

### Frontend
- **Framework:** Next.js 16+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Auth:** Better Auth (JWT)
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.13+
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Deployment:** Render/Railway

### Development
- **Spec-Driven:** Claude Code + Spec-Kit Plus
- **Containerization:** Docker Compose
- **Testing:** Pytest + Jest
- **CI/CD:** GitHub Actions

## 📁 Project Structure

```
├── frontend/       # Next.js application
├── backend/        # FastAPI server
├── specs/          # Feature specifications
├── history/        # PHRs and ADRs
└── .claude/        # Claude Code configuration
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.13+
- Neon Database account (free tier)
- Docker (optional)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd {project-name}
   ```

2. **Set up environment variables**

   **Frontend** (create `frontend/.env.local`):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   BETTER_AUTH_SECRET=your-secret-key-min-32-chars
   ```

   **Backend** (create `backend/.env`):
   ```env
   DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname
   BETTER_AUTH_SECRET=your-secret-key-min-32-chars
   OPENAI_API_KEY=sk-your-openai-api-key
   ```

3. **Install dependencies**

   **Frontend:**
   ```bash
   cd frontend
   npm install
   ```

   **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running Locally

**Option 1: Run services separately**

```bash
# Terminal 1 - Frontend
cd frontend
npm run dev
# → http://localhost:3000

# Terminal 2 - Backend
cd backend
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs (API docs)
```

**Option 2: Run with Docker Compose**

```bash
docker-compose up
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest                    # Run all tests
pytest --cov             # With coverage report
pytest -v                # Verbose output
```

### Frontend Tests
```bash
cd frontend
npm test                 # Run tests
npm run test:watch      # Watch mode
```

## 🌐 API Documentation

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### API Endpoints

```
GET    /api/{user_id}/tasks              List all tasks
POST   /api/{user_id}/tasks              Create task
GET    /api/{user_id}/tasks/{id}         Get task
PUT    /api/{user_id}/tasks/{id}         Update task
DELETE /api/{user_id}/tasks/{id}         Delete task
PATCH  /api/{user_id}/tasks/{id}/complete Toggle completion
```

## 📚 Development Workflow

### Spec-Driven Development

This project follows spec-driven development principles:

1. **Write Specification**
   ```bash
   # Use spec-writer skill
   "Use spec-writer skill to create task CRUD spec"
   ```

2. **Generate Code**
   ```bash
   # Backend
   "Use fastapi-sqlmodel skill from @specs/features/task-crud.md"

   # Frontend
   "Use nextjs-auth skill from @specs/ui/task-management.md"
   ```

3. **Test & Iterate**
   ```bash
   pytest
   npm test
   ```

4. **Document**
   ```bash
   /sp.phr  # Create Prompt History Record
   ```

## 🚀 Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables
4. Deploy

```bash
cd frontend
vercel deploy
```

### Backend (Render/Railway)

1. Connect GitHub repository
2. Set environment variables:
   - `DATABASE_URL`
   - `BETTER_AUTH_SECRET`
   - `OPENAI_API_KEY`
3. Deploy from main branch

## 📝 Documentation

- **Specifications:** `/specs/features/`
- **API Docs:** `/specs/api/rest-endpoints.md`
- **Database Schema:** `/specs/database/schema.md`
- **Frontend Guide:** `frontend/CLAUDE.md`
- **Backend Guide:** `backend/CLAUDE.md`

## 🤝 Contributing

This project follows spec-driven development. All changes must:

1. Have a specification in `/specs`
2. Pass all tests
3. Include a PHR in `/history/prompts`
4. Follow code conventions in CLAUDE.md files

## 📋 Hackathon Submission

### Required Deliverables
- ✅ Public GitHub repository
- ✅ Deployed frontend (Vercel)
- ✅ Deployed backend (Render/Railway)
- ✅ Demo video (< 90 seconds)
- ✅ All specifications documented

### Submission Form
Submit at: https://forms.gle/KMKEKaFUD6ZX4UtY8

## 📄 License

MIT

## 👤 Author

{Author Name}

---

**Built with spec-driven development using Claude Code!** 🚀
```

### 6. Root .gitignore
```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.venv/
venv/
env/
ENV/

# Build outputs
.next/
out/
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Database
*.db
*.sqlite
*.sqlite3

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/
coverage/

# Misc
.vercel
.temp/
tmp/
```

### 7. Frontend package.json
```json
{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "better-auth": "^1.0.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "typescript": "^5",
    "tailwindcss": "^3.4.0",
    "postcss": "^8",
    "autoprefixer": "^10",
    "eslint": "^8",
    "eslint-config-next": "^16.0.0"
  }
}
```

### 8. Backend requirements.txt
```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlmodel==0.0.22
psycopg2-binary==2.9.10
pydantic==2.10.0
pydantic-settings==2.6.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.12
pytest==8.3.0
pytest-cov==6.0.0
httpx==0.27.0
```

## Usage Example

```markdown
**User:** Use monorepo-structure skill to create Phase 2 project structure for "todo-app"

**Claude:** Creating complete Phase 2 monorepo structure for todo-app...

✅ Created 50+ files and folders:
  📁 Frontend (Next.js 16+)
  📁 Backend (FastAPI + SQLModel)
  📁 Specs (Organized by type)
  📁 History (PHRs + ADRs)
  📁 .claude (Skills + commands)
  📄 Configuration files
  📄 Documentation files

✅ Structure follows:
  - Spec-Kit Plus conventions
  - Hackathon Phase 2 requirements
  - Best practices for monorepos

Ready to start development! Next steps:
1. Set up environment variables
2. Install dependencies
3. Use spec-writer skill to create specs
4. Use code generation skills to build features

**Project ready in 2 minutes!** 🚀
```

## Best Practices

### 1. Clear Separation
- Frontend and backend completely separated
- Each has own CLAUDE.md and README
- Shared specs in `/specs`

### 2. Spec-Kit Plus Compliance
- Specs organized by type
- PHRs in `/history/prompts`
- ADRs in `/history/adr`

### 3. Ready-to-Use Configuration
- All config files included
- Environment templates provided
- Docker setup ready

### 4. Documentation
- Comprehensive README
- CLAUDE.md at each level
- Inline documentation

## Time Savings

**Manual Setup:**
- Creating folders: 30 minutes
- Writing config files: 1-2 hours
- Documentation: 1 hour
- **Total: 2.5-3.5 hours**

**With This Skill:**
- Generation: 2-3 minutes
- Review: 5-10 minutes
- **Total: 10-15 minutes**

**Time Saved: 95%+** ⚡

## Reusability

Use for:
- Phase 2 (Full-Stack Web App)
- Phase 3 (AI Chatbot)
- Phase 4 (Kubernetes Deployment)
- Phase 5 (Advanced Cloud)
- Future full-stack projects

## Success Metrics

Generated structure should:
- ✅ Follow Spec-Kit Plus conventions
- ✅ Include all required configuration
- ✅ Have comprehensive documentation
- ✅ Be ready for immediate development
- ✅ Support spec-driven workflow

---

**Create production-ready monorepos in minutes!** 🏗️
