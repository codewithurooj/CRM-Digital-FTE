# Claude Code Rules — CRM Digital FTE

## Project Overview

**Project**: CRM Digital FTE (Customer Success AI Employee)
**Type**: Hackathon 5 — Build a 24/7 AI Customer Support Agent
**Duration**: 48-72 Development Hours | Solo Developer

### What This Project Does

An AI-powered Customer Success agent (Digital Full-Time Equivalent) that:
- Handles customer support queries **24/7 autonomously** across 3 channels
- **Gmail** — receives emails via Gmail API + Pub/Sub, replies via Gmail API
- **WhatsApp** — receives messages via Twilio webhook, replies via Twilio API
- **Web Support Form** — React/Next.js form submitting to FastAPI backend
- Identifies the **same customer across channels** (email on Gmail = same person on WhatsApp)
- Creates tickets, searches a knowledge base, and escalates when needed
- Tracks all interactions in a PostgreSQL-based CRM (no external CRM)
- Streams events through Kafka for async processing
- Deploys on Kubernetes for 24/7 uptime with auto-scaling

### Business Context

Replaces a $75k/year human support agent with an AI agent costing <$1k/year.
The agent is for a fictional SaaS company ("TechCorp") whose product docs,
company profile, and sample tickets live in the `context/` folder.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.11+ | Backend, agent, workers |
| **AI Agent** | OpenAI Agents SDK | `@function_tool` pattern, GPT-4o |
| **API** | FastAPI + uvicorn | REST endpoints, webhook handlers |
| **Database** | PostgreSQL 16 + pgvector | CRM tables + vector search for knowledge base |
| **DB Driver** | asyncpg | Async PostgreSQL access |
| **Streaming** | Apache Kafka (aiokafka) | Decouple channel intake from agent processing |
| **Frontend** | React / Next.js | Web Support Form component only |
| **Email** | Gmail API | OAuth2 + Pub/Sub push notifications |
| **Messaging** | Twilio WhatsApp API | Webhook + REST for WhatsApp |
| **Testing** | pytest + pytest-asyncio + httpx | TDD mandatory, 80% coverage gate |
| **Load Test** | Locust | 24/7 readiness validation |
| **Container** | Docker | Multi-stage builds |
| **Orchestration** | Kubernetes (minikube) | Production deployment |

## Project Structure

```
CRM-Digital-FTE/
├── context/                    # Fake SaaS company context (knowledge base source)
│   ├── company-profile.md
│   ├── product-docs.md
│   ├── sample-tickets.json
│   ├── escalation-rules.md
│   └── brand-voice.md
├── production/
│   ├── agent/                  # AI agent (OpenAI Agents SDK)
│   │   ├── customer_success_agent.py
│   │   ├── tools.py            # @function_tool definitions
│   │   ├── prompts.py          # System prompts
│   │   └── formatters.py       # Channel-specific response formatting
│   ├── channels/               # Channel integrations
│   │   ├── gmail_handler.py
│   │   ├── whatsapp_handler.py
│   │   └── web_form_handler.py
│   ├── workers/                # Kafka consumers
│   │   ├── message_processor.py
│   │   └── metrics_collector.py
│   ├── api/                    # FastAPI application
│   │   └── main.py
│   ├── database/               # PostgreSQL schema + queries
│   │   ├── schema.sql
│   │   ├── migrations/
│   │   └── queries.py
│   ├── kafka_client.py         # Kafka producer/consumer
│   ├── tests/                  # All tests (TDD)
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── contract/
│   │   ├── e2e/
│   │   └── load/
│   ├── k8s/                    # Kubernetes manifests
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── web-form/                   # React/Next.js Support Form
│   └── SupportForm.jsx
├── specs/                      # Hackathon deliverable specs
│   ├── discovery-log.md
│   └── customer-success-fte-spec.md
├── .specify/                   # SDD templates and scripts
│   └── memory/constitution.md  # Project constitution (8 principles)
├── history/                    # PHRs and ADRs
│   ├── prompts/
│   └── adr/
├── CLAUDE.md                   # This file
└── .gitignore
```

## Database Schema (PostgreSQL = Your CRM)

Key tables — no external CRM needed:
- `customers` — unified customer records (email + phone)
- `customer_identifiers` — cross-channel identity matching
- `conversations` — conversation threads with channel tracking
- `messages` — all messages (inbound + outbound) with channel metadata
- `tickets` — support tickets with status lifecycle
- `knowledge_base` — product docs with pgvector embeddings for semantic search
- `channel_configs` — per-channel settings
- `agent_metrics` — performance tracking

## Core Architecture

```
Gmail Webhook ──┐
WhatsApp Hook ──┼──→ Kafka (fte.tickets.incoming) ──→ Worker Pod ──→ Agent ──→ Response
Web Form POST ──┘         (async, decoupled)          (consumer)    (GPT-4o)   (via channel)
```

- Webhooks publish to Kafka and return immediately (< 500ms)
- Worker pods consume from Kafka, run the agent, store results in PostgreSQL
- Agent uses 5 tools: search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, send_response
- Responses formatted per channel (email: formal, WhatsApp: concise, web: semi-formal)

## Constitution Principles (v1.1.0)

See `.specify/memory/constitution.md` for full details. Summary:

1. **Production-First** — no throwaway prototypes
2. **Channel-Agnostic Core** — agent + DB are channel-unaware; channels are pluggable
3. **TDD (NON-NEGOTIABLE)** — Red-Green-Refactor, 80% coverage gate
4. **Database as Source of Truth** — all state in PostgreSQL
5. **Async Pipeline** — Kafka decouples intake from processing
6. **Fail Gracefully** — never lose a customer message
7. **Secrets in Environment** — zero hardcoded credentials
8. **Smallest Viable Diff** — build incrementally along dependency chain

## Development Methodology

### TDD — Red-Green-Refactor (Mandatory)

Every feature follows this cycle:
1. **RED**: Write a failing test
2. **GREEN**: Write minimum code to pass
3. **REFACTOR**: Clean up while tests stay green

Coverage: `pytest --cov=src --cov-fail-under=80`

### Build Order (Dependency Chain)

```
Step 1: Context files → Step 2: Database → Step 3: Agent → Step 4: Web Form
→ Step 5: Kafka → Step 6: Gmail → Step 7: WhatsApp → Step 8: K8s → Step 9: Tests/Docs
```

### Agent Guardrails (Hard Constraints)

- NEVER discuss pricing → escalate immediately
- NEVER promise features not in documentation
- NEVER process refunds → escalate to billing
- ALWAYS create ticket BEFORE responding
- ALWAYS format response per channel
- ALWAYS check sentiment before closing

## SDD Agent Instructions

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architect to build this CRM Digital FTE.

**Your Success is Measured By:**
- All outputs strictly follow user intent
- TDD cycle enforced: tests written BEFORE implementation
- PHRs created for every significant interaction
- ADR suggestions made for architectural decisions
- All changes are small, testable, and reference code precisely

### Core Guarantees

- Record every user input in a PHR after every user message
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when architecturally significant decisions are detected, suggest documenting them. Never auto-create ADRs.

### Development Guidelines

1. **Authoritative Source Mandate**: Use MCP tools and CLI commands for information gathering. NEVER assume from internal knowledge.
2. **TDD Enforcement**: Always write tests first. Refuse to write implementation without a failing test.
3. **PHR for Every Input**: Create a Prompt History Record after completing requests.
4. **ADR Suggestions**: Surface architectural decisions for documentation.
5. **Human as Tool**: Ask the user when requirements are ambiguous or multiple valid approaches exist.

### PHR Creation Process

1. Detect stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general
2. Generate title (3-7 words, slug for filename)
3. Route: constitution → `history/prompts/constitution/`, feature → `history/prompts/<feature>/`, general → `history/prompts/general/`
4. Read template from `.specify/templates/phr-template.prompt.md`
5. Fill ALL placeholders, write file
6. Validate: no unresolved placeholders, path matches route

### Default Policies

- Clarify and plan first
- Do not invent APIs or contracts; ask if missing
- Never hardcode secrets — use `.env`
- Prefer smallest viable diff
- Cite existing code with references (start:end:path)
- Keep reasoning private; output decisions and artifacts

### Execution Contract

1. Confirm surface and success criteria
2. List constraints, invariants, non-goals
3. Produce artifact with acceptance checks
4. Follow-ups and risks (max 3 bullets)
5. Create PHR
6. Surface ADR suggestions if applicable

## Architect Guidelines

When planning, address:
1. Scope and Dependencies (in/out of scope, external deps)
2. Key Decisions and Rationale
3. Interfaces and API Contracts
4. Non-Functional Requirements (performance, reliability, security, cost)
5. Data Management and Migration
6. Operational Readiness (observability, alerting, runbooks, deployment)
7. Risk Analysis (top 3 risks, blast radius, kill switches)
8. Evaluation (definition of done, output validation)
9. ADRs for significant decisions

### ADR Significance Test

- Impact: long-term consequences?
- Alternatives: multiple viable options considered?
- Scope: cross-cutting, influences system design?

If ALL true, suggest: "Architectural decision detected: [brief]. Document? Run `/sp.adr [title]`"

## Scoring Rubric (100 points)

| Category | Points | Key Requirements |
|----------|--------|-----------------|
| Incubation Quality | 10 | Discovery log, iterative exploration |
| Agent Implementation | 10 | All tools work, channel-aware, error handling |
| **Web Support Form** | **10** | **Complete React form — REQUIRED** |
| Channel Integrations | 10 | Gmail + WhatsApp handlers |
| Database + Kafka | 5 | Schema, channel tracking, streaming |
| Kubernetes | 5 | Manifests, scaling, health checks |
| 24/7 Readiness | 10 | Pod restarts, scaling, no SPOF |
| Cross-Channel | 10 | Customer ID across channels, history preserved |
| Monitoring | 5 | Channel metrics, alerts |
| Customer Experience | 10 | Channel-appropriate responses, escalation |
| Documentation | 5 | Deployment guide, API docs |
| Innovation | 10 | Novel approaches, clear evolution |

## Code Standards

See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.
