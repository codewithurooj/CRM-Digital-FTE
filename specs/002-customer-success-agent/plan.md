# Implementation Plan: Customer Success AI Agent (Digital FTE)

**Branch**: `002-customer-success-agent` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-customer-success-agent/spec.md`

## Summary

Build a 24/7 AI Customer Success agent that autonomously handles support across 3 channels (Web Form, Gmail, WhatsApp) with unified cross-channel identity, Kafka-based async processing, a PostgreSQL CRM with pgvector semantic search, and Kubernetes deployment with auto-scaling. The agent uses the OpenAI Agents SDK with 5 `@function_tool` definitions, enforces strict guardrails (no pricing/refunds/false promises), and formats responses per channel.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI + uvicorn, OpenAI Agents SDK, aiokafka, asyncpg, google-api-python-client, twilio
**Frontend**: React / Next.js (Web Support Form component only)
**Storage**: PostgreSQL 16 + pgvector extension (CRM + vector search)
**Testing**: pytest + pytest-asyncio + httpx + pytest-cov (80% coverage gate)
**Target Platform**: Kubernetes (minikube for dev), Docker multi-stage builds
**Project Type**: Web application (Python backend + React frontend)
**Performance Goals**: Webhook response < 500ms, agent processing < 3s p95, end-to-end delivery < 30s, 99.9% uptime
**Constraints**: < 500ms webhook latency, 80% test coverage, TDD mandatory, all state in PostgreSQL
**Scale/Scope**: 100+ web form submissions + 50+ emails + 50+ WhatsApp messages over 24h test period

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Production-First | PASS | All code targets production architecture. Context files serve as knowledge base seed, not throwaway scripts. |
| II | Channel-Agnostic Core | PASS | Agent core and DB layer are channel-unaware. Channel handlers in `production/channels/` normalize inbound and format outbound. Adding a channel = adding one handler file. |
| III | TDD (NON-NEGOTIABLE) | PASS | Build order includes test-first for every component. pytest + pytest-asyncio + httpx. 80% coverage gate enforced. |
| IV | Database as Source of Truth | PASS | All state in PostgreSQL — customers, conversations, messages, tickets, knowledge base. No in-memory-only state. |
| V | Async Pipeline (Kafka) | PASS | Webhooks publish to Kafka and return immediately. Worker pods consume and process. Dead-letter queue for failures. |
| VI | Fail Gracefully | PASS | Every error → apologetic response + DLQ publish + structured logging. Agent failures never surface raw errors. |
| VII | Secrets in Environment | PASS | All API keys, credentials, tokens from env vars or K8s Secrets. Non-secret config in ConfigMaps with sensible defaults. |
| VIII | Smallest Viable Diff | PASS | Build order follows dependency chain: Context → DB → Agent → Web Form → Kafka → Gmail → WhatsApp → K8s. Each step produces a working, testable increment. |

**Gate Result**: ALL PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-customer-success-agent/
├── plan.md              # This file
├── research.md          # Phase 0 output — technology decisions
├── data-model.md        # Phase 1 output — PostgreSQL schema (8 tables)
├── quickstart.md        # Phase 1 output — local dev setup
├── contracts/           # Phase 1 output — API contracts
│   ├── web-form.md      # POST /api/v1/support/form
│   ├── gmail-webhook.md # POST /api/v1/webhooks/gmail
│   ├── whatsapp-webhook.md # POST /api/v1/webhooks/whatsapp
│   ├── health.md        # GET /api/v1/health
│   ├── metrics.md       # GET /api/v1/metrics/channels
│   └── tickets.md       # GET /api/v1/tickets/{ticket_id}
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
production/
├── context/                        # TechCorp knowledge base source files
│   ├── company-profile.md
│   ├── product-docs.md
│   ├── sample-tickets.json
│   ├── escalation-rules.md
│   └── brand-voice.md
├── agent/                          # AI agent (OpenAI Agents SDK)
│   ├── __init__.py
│   ├── customer_success_agent.py   # Agent definition + runner
│   ├── tools.py                    # 5 @function_tool definitions
│   ├── prompts.py                  # System prompts (channel-aware)
│   └── formatters.py               # Channel-specific response formatting
├── channels/                       # Channel adapters (normalize in, format out)
│   ├── __init__.py
│   ├── base.py                     # Abstract channel handler interface
│   ├── gmail_handler.py            # Gmail API + Pub/Sub webhook
│   ├── whatsapp_handler.py         # Twilio webhook + API
│   └── web_form_handler.py         # FastAPI form endpoint
├── workers/                        # Kafka consumers
│   ├── __init__.py
│   ├── message_processor.py        # Main worker: consume → agent → respond
│   └── metrics_collector.py        # Metrics aggregation worker
├── api/                            # FastAPI application
│   ├── __init__.py
│   ├── main.py                     # App factory, middleware, CORS
│   ├── router.py                   # Route registration
│   ├── dependencies.py             # Shared dependencies (DB pool, Kafka producer)
│   └── endpoints/
│       ├── __init__.py
│       ├── health.py               # GET /api/v1/health
│       ├── metrics.py              # GET /api/v1/metrics/channels
│       ├── support_form.py         # POST /api/v1/support/form
│       ├── tickets.py              # GET /api/v1/tickets/{ticket_id}
│       ├── gmail_webhook.py        # POST /api/v1/webhooks/gmail
│       └── whatsapp_webhook.py     # POST /api/v1/webhooks/whatsapp
├── database/                       # PostgreSQL layer
│   ├── __init__.py
│   ├── pool.py                     # asyncpg connection pool (lazy singleton)
│   ├── schema.sql                  # DDL for all 8 tables
│   ├── seed.sql                    # Channel configs + knowledge base seed
│   ├── migrations/                 # Manual migration scripts
│   └── queries/
│       ├── __init__.py
│       ├── customers.py            # Customer CRUD + identity resolution
│       ├── conversations.py        # Conversation lifecycle
│       ├── messages.py             # Message storage + retrieval
│       ├── tickets.py              # Ticket CRUD + status transitions
│       ├── knowledge_base.py       # Vector search + CRUD
│       └── metrics.py              # Metrics recording + aggregation
├── kafka_client.py                 # Kafka producer/consumer factory
├── config.py                       # Pydantic Settings (env-based config)
├── schemas/                        # Pydantic models (request/response)
│   ├── __init__.py
│   ├── support_form.py
│   ├── messages.py
│   ├── tickets.py
│   ├── health.py
│   └── metrics.py
├── tests/
│   ├── conftest.py                 # Fixtures: test DB, mock Kafka, mock OpenAI
│   ├── unit/
│   │   ├── test_config.py
│   │   ├── test_agent_tools.py
│   │   ├── test_formatters.py
│   │   ├── test_prompts.py
│   │   ├── test_identity_resolution.py
│   │   └── test_guardrails.py
│   ├── integration/
│   │   ├── test_database_queries.py
│   │   ├── test_support_form_api.py
│   │   ├── test_health_api.py
│   │   ├── test_ticket_api.py
│   │   └── test_kafka_pipeline.py
│   ├── contract/
│   │   ├── test_web_form_contract.py
│   │   ├── test_gmail_webhook_contract.py
│   │   ├── test_whatsapp_webhook_contract.py
│   │   └── test_health_contract.py
│   ├── e2e/
│   │   ├── test_web_form_e2e.py
│   │   ├── test_gmail_e2e.py
│   │   ├── test_whatsapp_e2e.py
│   │   └── test_cross_channel.py
│   └── load/
│       └── locustfile.py
├── k8s/
│   ├── namespace.yaml
│   ├── secrets.yaml
│   ├── configmap.yaml
│   ├── postgres-deployment.yaml
│   ├── kafka-deployment.yaml
│   ├── api-deployment.yaml
│   ├── worker-deployment.yaml
│   ├── api-hpa.yaml
│   └── worker-hpa.yaml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── requirements-dev.txt

web-form/                           # React/Next.js Support Form
├── package.json
├── src/
│   ├── components/
│   │   ├── SupportForm.jsx         # Main form component
│   │   ├── FormField.jsx           # Reusable input field
│   │   ├── StatusChecker.jsx       # Ticket status lookup
│   │   └── SuccessMessage.jsx      # Post-submission confirmation
│   ├── hooks/
│   │   └── useFormValidation.js    # Client-side validation
│   ├── services/
│   │   └── api.js                  # API client for form submission
│   └── App.jsx
└── tests/
    └── SupportForm.test.jsx
```

**Structure Decision**: Web application pattern — Python backend (`production/`) with separate React frontend (`web-form/`). The backend houses the agent, channels, workers, API, database layer, and K8s manifests. The frontend is a standalone embeddable component.

## Architecture

### High-Level Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Web Form   │     │ Gmail Pub/  │     │   Twilio    │
│  (React)    │     │ Sub Push    │     │  WhatsApp   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI API Pods (3-20 replicas)        │
│                                                     │
│  POST /support/form  POST /webhooks/  POST /webhooks│
│                       gmail           /whatsapp     │
│                                                     │
│  1. Validate input                                  │
│  2. Normalize to unified message format             │
│  3. Publish to Kafka fte.tickets.incoming            │
│  4. Return immediately (< 500ms)                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│           Apache Kafka (fte.tickets.incoming)        │
│                                                     │
│  Message format: {                                  │
│    customer_identifier, channel, content,            │
│    metadata, timestamp                               │
│  }                                                  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│          Worker Pods (3-30 replicas)                 │
│                                                     │
│  1. Consume message from Kafka                      │
│  2. Resolve customer identity (DB lookup)           │
│  3. Create/resume conversation                      │
│  4. Run AI Agent:                                   │
│     a. create_ticket (always first)                 │
│     b. get_customer_history                         │
│     c. search_knowledge_base (pgvector)             │
│     d. send_response (formatted per channel)        │
│     e. escalate_to_human (if triggered)             │
│  5. Store response in DB                            │
│  6. Route response to outbound channel              │
│  7. Commit Kafka offset                             │
│                                                     │
│  On error:                                          │
│  → Send apologetic message to customer              │
│  → Publish to fte.tickets.dlq                       │
│  → Log structured error                             │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌────────────┐ ┌────────┐ ┌──────────┐
   │  Gmail API │ │ Twilio │ │  DB +    │
   │  (reply in │ │  API   │ │  API     │
   │   thread)  │ │        │ │ (stored  │
   │            │ │        │ │ response)│
   └────────────┘ └────────┘ └──────────┘
```

### Cross-Channel Identity Resolution

```
Inbound message arrives with identifier (email or phone)
        │
        ▼
┌─────────────────────────────────────┐
│ Query customer_identifiers table    │
│ WHERE identifier_value = ?          │
└───────────────┬─────────────────────┘
                │
        ┌───────┴───────┐
        │  Found?       │
        └───────┬───────┘
         Yes    │    No
          │     │     │
          ▼     │     ▼
   Return       │  ┌──────────────────────┐
   customer_id  │  │ Query customers      │
                │  │ WHERE email = ?       │
                │  │ (for WhatsApp, check  │
                │  │  profile email)       │
                │  └──────────┬───────────┘
                │        Found? │
                │    Yes │   No │
                │      ▼      ▼
                │  Link ID  Create new
                │  to       customer +
                │  existing identifier
                │  customer
```

### Agent Tool Execution Order

The agent follows a strict tool execution sequence enforced by the system prompt:

```
1. create_ticket()           — ALWAYS first, before any response
2. get_customer_history()    — Check prior interactions
3. search_knowledge_base()   — Semantic search via pgvector (up to 2 attempts)
4. send_response()           — Format per channel, deliver
   OR
4. escalate_to_human()       — If guardrails triggered or KB empty after 2 tries
```

### Guardrail Check Flow

```
Customer message arrives
        │
        ▼
┌──────────────────────────┐
│ Check hard triggers:     │
│ • Pricing keywords       │
│ • Refund keywords        │
│ • Legal language          │
│ • Explicit human request │
│ • Profanity / ALL CAPS   │
└───────────┬──────────────┘
            │
     Trigger found?
      Yes │    │ No
          ▼    ▼
   Escalate   Continue to
   immediately KB search
              │
         Found relevant?
          Yes │    │ No (after 2 tries)
              ▼    ▼
         Respond  Escalate
              │
         Check sentiment
         before closing
         (< 0.3 → escalate)
```

### Kafka Topic Design

| Topic | Purpose | Producers | Consumers |
|-------|---------|-----------|-----------|
| `fte.tickets.incoming` | All inbound messages (normalized) | API pods (webhook handlers) | Worker pods |
| `fte.tickets.outgoing` | Agent responses routed to channels | Worker pods | Channel-specific delivery workers |
| `fte.tickets.dlq` | Failed messages for human review | Worker pods (on error) | Ops dashboard / manual review |

### Kubernetes Deployment Architecture

```
┌─ Namespace: crm-digital-fte ──────────────────────────────────┐
│                                                                │
│  ┌─ Deployment: api ─────────┐  ┌─ Deployment: worker ──────┐ │
│  │ Replicas: 3-20 (HPA)     │  │ Replicas: 3-30 (HPA)     │ │
│  │ CPU target: 70%           │  │ CPU target: 70%           │ │
│  │ Probes: /health           │  │ Probes: /health           │ │
│  │ Port: 8000                │  │ (Kafka consumer health)   │ │
│  └───────────────────────────┘  └───────────────────────────┘ │
│                                                                │
│  ┌─ StatefulSet: postgres ───┐  ┌─ StatefulSet: kafka ──────┐ │
│  │ Replicas: 1               │  │ Replicas: 1 (+ ZooKeeper) │ │
│  │ PVC: 10Gi                 │  │ PVC: 5Gi                  │ │
│  │ Port: 5432                │  │ Port: 9092                │ │
│  └───────────────────────────┘  └───────────────────────────┘ │
│                                                                │
│  ┌─ Secret: crm-secrets ─────────────────────────────────────┐ │
│  │ OPENAI_API_KEY, GMAIL_CREDENTIALS, TWILIO_AUTH_TOKEN,     │ │
│  │ DATABASE_URL, KAFKA_BOOTSTRAP_SERVERS                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌─ ConfigMap: crm-config ───────────────────────────────────┐ │
│  │ LOG_LEVEL, ENABLED_CHANNELS, MAX_RESPONSE_LENGTHS,        │ │
│  │ ESCALATION_THRESHOLDS                                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌─ Service: api-service ────┐  ┌─ Service: postgres-svc ───┐ │
│  │ Type: ClusterIP           │  │ Type: ClusterIP           │ │
│  │ Port: 80 → 8000           │  │ Port: 5432               │ │
│  └───────────────────────────┘  └───────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

## Build Order (Dependency Chain)

Following Constitution Principle VIII — each step produces a working, testable increment.

| Step | Component | Depends On | Deliverable | Test Coverage |
|------|-----------|------------|-------------|---------------|
| 1 | Context files | — | Knowledge base source material in `production/context/` | Validation tests (files exist, valid JSON/MD) |
| 2 | Database schema + queries | Step 1 | PostgreSQL DDL, asyncpg pool, CRUD queries for all 8 tables | Unit tests (queries), integration tests (real PG via Docker) |
| 3 | AI Agent + tools | Step 2 | OpenAI Agents SDK agent with 5 @function_tool definitions | Unit tests (mocked OpenAI), guardrail tests, formatter tests |
| 4 | Web Support Form | Steps 2, 3 | React form + FastAPI POST endpoint + ticket status endpoint | Contract tests, integration tests, React component tests |
| 5 | Kafka pipeline | Steps 2, 3, 4 | aiokafka producer/consumer, message processor worker | Integration tests (embedded Kafka or mocked), E2E tests |
| 6 | Gmail integration | Steps 2, 3, 5 | Gmail Pub/Sub webhook handler, Gmail API reply sender | Contract tests (webhook shape), integration tests (mocked Gmail API) |
| 7 | WhatsApp integration | Steps 2, 3, 5 | Twilio webhook handler, Twilio API sender | Contract tests (Twilio signature), integration tests (mocked Twilio) |
| 8 | Kubernetes deployment | Steps 1-7 | K8s manifests, Dockerfile, docker-compose.yml | Deployment smoke tests, pod health checks |
| 9 | Monitoring + metrics | Steps 2, 5 | /health endpoint, /metrics/channels, agent_metrics recording | Integration tests, load tests (Locust) |

## Complexity Tracking

No constitution violations to justify. All decisions align with the 8 principles.

## Key Design Decisions

### 1. asyncpg over SQLAlchemy ORM

Raw asyncpg with hand-written SQL. The schema is stable (8 tables, defined upfront), and asyncpg provides 2-3x better performance. pgvector queries are simpler in raw SQL. See [research.md](./research.md) for full rationale.

### 2. Unified Message Format

All channels normalize inbound messages to a single Pydantic model before publishing to Kafka:

```python
class InboundMessage(BaseModel):
    customer_identifier: str      # email or phone number
    identifier_type: str          # "email" or "phone"
    channel: str                  # "email", "whatsapp", "web_form"
    content: str                  # message body
    subject: str | None = None    # email/web form subject
    metadata: dict = {}           # channel-specific (gmail thread ID, twilio SID)
    timestamp: datetime
```

### 3. Lazy Initialization Pattern

Database pool, Kafka producer, and OpenAI client use lazy singletons (not module-level). This enables test imports without triggering real connections. See memory notes on this pattern.

### 4. Channel Adapter Interface

```python
class ChannelHandler(ABC):
    @abstractmethod
    async def parse_inbound(self, raw_data: dict) -> InboundMessage: ...

    @abstractmethod
    async def format_response(self, response: str, metadata: dict) -> str: ...

    @abstractmethod
    async def deliver(self, formatted: str, destination: str, metadata: dict) -> bool: ...
```

Each channel implements this interface. The worker calls `parse_inbound` → agent → `format_response` → `deliver`.

### 5. Ticket Number Generation

Database-level sequence + trigger generates `TKT-XXXX` format ticket numbers. No application-level coordination needed. See [data-model.md](./data-model.md).

## Non-Functional Requirements

| Category | Requirement | Implementation |
|----------|-------------|----------------|
| **Performance** | Webhook < 500ms | Publish to Kafka and return. No agent processing in webhook path. |
| **Performance** | Agent response < 3s p95 | GPT-4o with streaming, cached knowledge base embeddings |
| **Performance** | End-to-end < 30s | Kafka consumer latency + agent processing + channel delivery |
| **Reliability** | 99.9% uptime | K8s with liveness/readiness probes, auto-restart, HPA |
| **Reliability** | Zero message loss | Kafka consumer commits offset only after successful processing. DLQ for failures. |
| **Security** | No hardcoded secrets | All credentials from env vars / K8s Secrets |
| **Security** | Twilio signature validation | Verify X-Twilio-Signature on every WhatsApp webhook |
| **Security** | Input validation | Pydantic models validate all API inputs. SQL parameterized via asyncpg. |
| **Scalability** | API pods: 3-20 | HPA scales on CPU > 70% |
| **Scalability** | Worker pods: 3-30 | HPA scales on CPU > 70% |
| **Observability** | Per-channel metrics | agent_metrics table + /metrics/channels endpoint |
| **Cost** | < $1k/year | GPT-4o at projected volume (< 500 tickets/week) ≈ $50-100/month |

## Risk Analysis

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| 1 | OpenAI API latency spikes (>5s) | Medium | High — breaches 30s E2E SLA | Timeout after 10s, send fallback response, escalate to human |
| 2 | Cross-channel identity mismatch | Medium | Medium — breaks continuity scoring | Match on email first (most reliable), phone second. Log unmatched for review. |
| 3 | Kafka consumer lag under load | Low | Medium — delays responses | HPA scales workers. Monitor consumer lag metric. Alert at > 100 messages behind. |

## References

- [Feature Spec](./spec.md)
- [Research — Technology Decisions](./research.md)
- [Data Model — PostgreSQL Schema](./data-model.md)
- [API Contracts](./contracts/)
- [Constitution](../../.specify/memory/constitution.md)
- [TechCorp Company Profile](../../production/context/company-profile.md)
- [TechCorp Product Docs](../../production/context/product-docs.md)
- [Escalation Rules](../../production/context/escalation-rules.md)
- [Brand Voice Guide](../../production/context/brand-voice.md)
