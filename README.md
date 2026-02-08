<p align="center">
  <h1 align="center">CRM Digital FTE</h1>
  <p align="center">
    <strong>A 24/7 AI Customer Success agent that replaces a $75k/year support role with an autonomous, multi-channel AI employee costing less than $1k/year.</strong>
  </p>
  <p align="center">
    <a href="#quick-start">Quick Start</a> &bull;
    <a href="#architecture">Architecture</a> &bull;
    <a href="#api-endpoints">API</a> &bull;
    <a href="#database-schema">Database</a> &bull;
    <a href="#testing">Testing</a> &bull;
    <a href="#deployment">Deployment</a>
  </p>
</p>

---

## What Is This?

CRM Digital FTE (Digital Full-Time Equivalent) is an AI-powered customer support agent built for **TechCorp**, a fictional SaaS company. It handles support queries autonomously across three channels — **Gmail**, **WhatsApp**, and a **Web Support Form** — while maintaining a unified view of every customer across all channels.

The agent creates tickets, searches a knowledge base using semantic search, formats responses per channel, enforces guardrails, and escalates to humans when it should. Every interaction is persisted in a PostgreSQL-based CRM. No external CRM needed.

---

## Architecture

```
                         CRM Digital FTE — System Architecture

  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
  │  Gmail API   │   │  Twilio API   │   │  React Form  │
  │  (Pub/Sub)   │   │  (WhatsApp)   │   │  (Next.js)   │
  └──────┬───────┘   └──────┬────────┘   └──────┬────────┘
         │                  │                    │
         ▼                  ▼                    ▼
  ┌──────────────────────────────────────────────────────┐
  │              FastAPI  (Webhook Handlers)              │
  │   /webhooks/gmail   /webhooks/whatsapp   /support/form│
  │              < 500ms response SLA                     │
  └──────────────────────┬───────────────────────────────┘
                         │  publish
                         ▼
  ┌──────────────────────────────────────────────────────┐
  │          Apache Kafka  (fte.tickets.incoming)         │
  │              Async • Decoupled • Durable              │
  └──────────────────────┬───────────────────────────────┘
                         │  consume
                         ▼
  ┌──────────────────────────────────────────────────────┐
  │               Worker Pod (Message Processor)          │
  │                                                      │
  │   ┌────────────────────────────────────────────────┐ │
  │   │         OpenAI Agent  (GPT-4o)                 │ │
  │   │                                                │ │
  │   │   Tools:                                       │ │
  │   │   ├── search_knowledge_base (pgvector)         │ │
  │   │   ├── create_ticket                            │ │
  │   │   ├── get_customer_history                     │ │
  │   │   ├── escalate_to_human                        │ │
  │   │   └── send_response                            │ │
  │   │                                                │ │
  │   │   Guardrails:                                  │ │
  │   │   ├── Never discuss pricing                    │ │
  │   │   ├── Never promise undocumented features      │ │
  │   │   ├── Never process refunds                    │ │
  │   │   └── Always check sentiment before closing    │ │
  │   └────────────────────────────────────────────────┘ │
  └──────────────────────┬───────────────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────────────┐
  │        PostgreSQL 16  +  pgvector  (= The CRM)       │
  │                                                      │
  │   customers ─── customer_identifiers (cross-channel) │
  │   conversations ─── messages (inbound + outbound)    │
  │   tickets ─── knowledge_base (semantic search)       │
  │   channel_configs ─── agent_metrics (time-series)    │
  └──────────────────────────────────────────────────────┘
```

**Key design decisions:**
- Webhooks publish to Kafka and return immediately (< 500ms) — no blocking on AI processing
- Guardrails are checked **before** the LLM call to save cost on hard triggers
- Sentiment scoring is keyword-based (not LLM) for speed and determinism
- Cross-channel identity resolution links the same customer across email, WhatsApp, and web

---

## Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| Language | Python 3.11+ | Backend, agent, workers |
| AI Agent | OpenAI Agents SDK | `@function_tool` pattern, GPT-4o |
| API | FastAPI + uvicorn | REST endpoints, webhook handlers |
| Database | PostgreSQL 16 + pgvector | CRM tables + vector search (1536-dim embeddings) |
| DB Driver | asyncpg | Async PostgreSQL access |
| Streaming | Apache Kafka (aiokafka) | Decouple channel intake from agent processing |
| Frontend | React / Next.js | Web Support Form with validation + ticket status |
| Email | Gmail API | OAuth2 + Pub/Sub push notifications |
| Messaging | Twilio WhatsApp API | Webhook + REST |
| Testing | pytest + pytest-asyncio + httpx | TDD, 222 tests, 80%+ coverage gate |
| Load Testing | Locust | 24/7 readiness validation |
| Container | Docker | Multi-stage builds |
| Orchestration | Kubernetes (minikube) | Production deployment with HPA auto-scaling |

---

## Features

### Three Communication Channels
- **Gmail** — Receives emails via Gmail API + Pub/Sub push notifications, replies in the same thread
- **WhatsApp** — Twilio webhook intake, async reply via Twilio REST API, smart message splitting at sentence boundaries
- **Web Support Form** — React/Next.js form with real-time validation, category selection, and ticket status tracking

### AI Agent with 5 Tools
- `search_knowledge_base` — Semantic search over product docs using pgvector (cosine similarity)
- `create_ticket` — Auto-generates `TKT-XXXX` tickets before every response
- `get_customer_history` — Retrieves past conversations across all channels
- `escalate_to_human` — Triggered by guardrail violations or explicit customer request
- `send_response` — Channel-aware formatting (formal for email, concise for WhatsApp, semi-formal for web)

### Cross-Channel Identity
- Unified `customers` table with `customer_identifiers` for cross-channel matching
- A customer emailing from `lisa@company.com` is recognized as the same person messaging on WhatsApp
- Full conversation history preserved across channel switches

### Guardrails (Pre-LLM)
- Pricing discussions → immediate escalation
- Undocumented feature promises → blocked
- Refund requests → routed to billing
- Sentiment analysis on every interaction

### Monitoring & Metrics
- Per-channel metrics: conversation count, sentiment, escalation rate, response latency
- Configurable alert thresholds (escalation rate > 25%, latency > 3000ms)
- Time-series data in `agent_metrics` table

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for the web form)

### 1. Start Infrastructure

```bash
cd production
docker compose up -d
```

This launches:
- **PostgreSQL 16** with pgvector on port `5432` (auto-runs schema + seed data)
- **Apache Kafka** on port `9092` (with Zookeeper on `2181`)

### 2. Configure Environment

Create `production/.env`:

```env
# Database
DATABASE_URL=postgresql://crm_user:crm_password@localhost:5432/crm_digital_fte

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Gmail (OAuth2)
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REFRESH_TOKEN=your-refresh-token
GMAIL_PUBSUB_TOKEN=your-pubsub-verification-token

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155551000

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### 3. Install & Run Backend

```bash
cd production
pip install -r requirements.txt
uvicorn production.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Run Web Form (Optional)

```bash
cd web-form
npm install
npm run dev
```

### 5. Verify

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Submit a test ticket
curl -X POST http://localhost:8000/api/v1/support/form \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lisa Chen",
    "email": "lisa.chen@example.com",
    "subject": "How to set up automations?",
    "category": "how_to",
    "message": "I just upgraded to Starter and want to set up a Slack notification automation."
  }'
```

---

## API Endpoints

| Method | Path | Purpose | Auth | SLA |
|:-------|:-----|:--------|:-----|:----|
| `POST` | `/api/v1/support/form` | Submit web support form | None | < 500ms |
| `POST` | `/api/v1/webhooks/gmail` | Gmail Pub/Sub push notifications | Bearer token | < 500ms |
| `POST` | `/api/v1/webhooks/whatsapp` | Twilio WhatsApp webhook | Twilio signature | < 500ms |
| `GET` | `/api/v1/tickets/{ticket_id}` | Get ticket status + responses | None | - |
| `GET` | `/api/v1/metrics/channels` | Channel performance metrics | None | - |
| `GET` | `/api/v1/health` | System health check (K8s probe) | None | - |

### Example: Support Form Response

```json
{
  "ticket_id": "TKT-0006",
  "status": "received",
  "message": "Your support request has been received. Our team will respond within 30 minutes.",
  "created_at": "2026-02-08T14:30:00Z"
}
```

### Example: Health Check Response

```json
{
  "status": "healthy",
  "components": {
    "database": { "status": "healthy", "latency_ms": 2 },
    "kafka":    { "status": "healthy", "latency_ms": 5 },
    "gmail":    { "status": "healthy" },
    "whatsapp": { "status": "healthy" },
    "agent":    { "status": "healthy" }
  },
  "version": "0.1.0"
}
```

---

## Database Schema

PostgreSQL **is** the CRM. Eight tables, zero external dependencies:

| Table | Purpose | Key Fields |
|:------|:--------|:-----------|
| `customers` | Unified customer records | email, name, phone, company, plan |
| `customer_identifiers` | Cross-channel identity matching | customer_id, identifier_type, identifier_value, channel |
| `conversations` | Conversation threads | customer_id, channel, status, sentiment_score |
| `messages` | All messages (in + out) | conversation_id, direction, role, content, delivery_status |
| `tickets` | Support tickets (`TKT-XXXX`) | ticket_number, category, priority, status, source_channel |
| `knowledge_base` | Product docs + pgvector embeddings | title, content, category, embedding (vector 1536) |
| `channel_configs` | Per-channel settings | channel, tone, max_response_length |
| `agent_metrics` | Time-series performance data | metric_type, channel, value, recorded_at |

**Notable features:**
- Auto-generated `TKT-XXXX` ticket numbers via PostgreSQL trigger + sequence
- HNSW index on knowledge base embeddings for fast vector search
- `updated_at` triggers on all mutable tables
- CHECK constraints enforce valid enums at the database level

---

## Project Structure

```
CRM-Digital-FTE/
├── context/                          # TechCorp company context (knowledge base source)
│   ├── company-profile.md
│   ├── product-docs.md
│   ├── sample-tickets.json
│   ├── escalation-rules.md
│   └── brand-voice.md
├── production/
│   ├── agent/                        # AI agent (OpenAI Agents SDK)
│   │   ├── customer_success_agent.py #   Agent definition + runner
│   │   ├── tools.py                  #   5 @function_tool definitions
│   │   ├── prompts.py                #   System prompts + guardrails
│   │   └── formatters.py             #   Channel-specific response formatting
│   ├── channels/                     # Channel integrations
│   │   ├── base.py                   #   Abstract channel handler
│   │   ├── gmail_handler.py          #   Gmail API + Pub/Sub
│   │   ├── whatsapp_handler.py       #   Twilio webhook + REST
│   │   └── web_form_handler.py       #   Web form normalization
│   ├── workers/                      # Kafka consumers
│   │   ├── message_processor.py      #   Main message processing loop
│   │   └── metrics_collector.py      #   Metrics aggregation
│   ├── api/                          # FastAPI application
│   │   ├── main.py                   #   App factory + lifespan
│   │   ├── router.py                 #   Route registration
│   │   ├── dependencies.py           #   Dependency injection
│   │   └── endpoints/                #   Route handlers
│   │       ├── support_form.py
│   │       ├── gmail_webhook.py
│   │       ├── whatsapp_webhook.py
│   │       ├── tickets.py
│   │       ├── metrics.py
│   │       └── health.py
│   ├── database/                     # PostgreSQL
│   │   ├── schema.sql                #   Full schema (8 tables)
│   │   ├── seed.sql                  #   Knowledge base seed data
│   │   ├── pool.py                   #   asyncpg connection pool
│   │   └── queries/                  #   Query modules per entity
│   ├── schemas/                      # Pydantic models
│   ├── kafka_client.py               # Kafka producer/consumer
│   ├── config.py                     # Environment-based configuration
│   ├── tests/                        # 222 tests (TDD)
│   │   ├── unit/          (24 files) #   Isolated function tests
│   │   ├── contract/       (6 files) #   API shape validation
│   │   ├── integration/    (3 files) #   Component interaction
│   │   ├── e2e/            (4 files) #   Full pipeline tests
│   │   └── load/           (1 file)  #   Locust load tests
│   ├── k8s/                          # Kubernetes manifests
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── postgres-deployment.yaml
│   │   ├── kafka-deployment.yaml
│   │   ├── api-deployment.yaml
│   │   ├── api-hpa.yaml
│   │   ├── worker-deployment.yaml
│   │   └── worker-hpa.yaml
│   ├── Dockerfile                    # Multi-stage build
│   ├── docker-compose.yml            # Local dev (Postgres + Kafka)
│   └── requirements.txt
├── web-form/                         # React/Next.js Support Form
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── SupportForm.jsx       #   Main form with validation
│           ├── FormField.jsx         #   Reusable input component
│           ├── StatusChecker.jsx     #   Ticket status lookup
│           └── SuccessMessage.jsx    #   Submission confirmation
├── specs/                            # Design artifacts
│   └── 002-customer-success-agent/
│       ├── spec.md                   #   Feature specification
│       ├── plan.md                   #   Implementation plan
│       ├── tasks.md                  #   Task breakdown
│       └── contracts/                #   API contracts (6 endpoints)
├── .specify/memory/constitution.md   # Project constitution (8 principles)
├── history/prompts/                  # Prompt History Records
├── CLAUDE.md                         # Development rules
└── README.md                         # You are here
```

---

## Kubernetes Deployment

### Prerequisites

- [minikube](https://minikube.sigs.k8s.io/) or any K8s cluster
- `kubectl` configured

### Deploy

```bash
# Create namespace
kubectl apply -f production/k8s/namespace.yaml

# Deploy infrastructure
kubectl apply -f production/k8s/configmap.yaml
kubectl apply -f production/k8s/secrets.yaml
kubectl apply -f production/k8s/postgres-deployment.yaml
kubectl apply -f production/k8s/kafka-deployment.yaml

# Deploy application
kubectl apply -f production/k8s/api-deployment.yaml
kubectl apply -f production/k8s/worker-deployment.yaml

# Enable auto-scaling
kubectl apply -f production/k8s/api-hpa.yaml
kubectl apply -f production/k8s/worker-hpa.yaml
```

### 24/7 Readiness

- **Liveness probe**: `GET /api/v1/health` — restarts unhealthy pods
- **Readiness probe**: Same endpoint — removes pods from service during startup
- **HPA auto-scaling**: API and worker pods scale independently based on CPU/memory
- **No single point of failure**: Multiple replicas of API and worker pods
- **Durable messaging**: Kafka retains messages if workers are temporarily down

---

## Testing

Built with strict TDD (Red-Green-Refactor). Every feature has tests written **before** implementation.

### Run All Tests

```bash
cd production
python -m pytest tests/ -v
```

### Run by Category

```bash
# Unit tests (isolated, fast)
python -m pytest tests/unit/ -v

# Contract tests (API shape validation)
python -m pytest tests/contract/ -v

# Integration tests (component interaction)
python -m pytest tests/integration/ -v

# End-to-end tests (full pipeline)
python -m pytest tests/e2e/ -v

# Load tests (24/7 readiness)
cd tests/load && locust -f locustfile.py
```

### Coverage

```bash
python -m pytest tests/ --cov=production --cov-fail-under=80 --cov-report=term-missing
```

### Current Stats

| Metric | Value |
|:-------|:------|
| Total tests | **222** |
| Test files | **37** |
| Categories | Unit, Contract, Integration, E2E, Load |
| Coverage gate | 80% minimum (enforced) |

---

## Scoring Rubric Coverage

This project was built for **Hackathon 5: Build a 24/7 AI Customer Support Agent** (100 points).

| Category | Points | Status | Evidence |
|:---------|:------:|:------:|:---------|
| Incubation Quality | 10 | Done | `specs/discovery-log.md`, iterative spec-driven development |
| Agent Implementation | 10 | Done | 5 tools, guardrails, channel-aware formatting, error handling |
| **Web Support Form** | **10** | **Done** | React form with validation, category/priority selection, status checker |
| Channel Integrations | 10 | Done | Gmail (Pub/Sub + API), WhatsApp (Twilio webhook + REST) |
| Database + Kafka | 5 | Done | 8-table PostgreSQL schema, pgvector, Kafka async pipeline |
| Kubernetes | 5 | Done | 9 manifests, HPA auto-scaling, health probes |
| 24/7 Readiness | 10 | Done | Pod restarts, HPA scaling, Kafka durability, no SPOF |
| Cross-Channel | 10 | Done | `customer_identifiers` table, identity resolution, unified history |
| Monitoring | 5 | Done | `/metrics/channels` endpoint, per-channel stats, alert thresholds |
| Customer Experience | 10 | Done | Channel-appropriate tone, sentiment analysis, escalation paths |
| Documentation | 5 | Done | This README, API contracts, deployment guide |
| Innovation | 10 | Done | Pre-LLM guardrails, keyword sentiment (no LLM cost), MCP server, spec-driven development |
| **Total** | **100** | | |

---

## License

This project was built as a hackathon submission. All rights reserved.
