<!--
  Sync Impact Report
  ==================
  Version change: 1.0.0 → 1.1.0 (MINOR — new principle added)
  Modified principles:
    - III–VII renumbered to IV–VIII
  Added sections:
    - Principle III: Test-Driven Development (NON-NEGOTIABLE)
    - Testing framework added to Required Stack table
    - Coverage gate added to Hard Constraints
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md — ✅ no changes needed
    - .specify/templates/spec-template.md — ✅ compatible
    - .specify/templates/tasks-template.md — ✅ compatible (test-first ordering preserved)
  Follow-up TODOs: None
-->

# CRM Digital FTE Constitution

## Core Principles

### I. Production-First — No Throwaway Code

Every line of code written MUST target the production architecture.
Prototyping is done through production components, not separate scripts.
The context files (company-profile, product-docs, sample-tickets) serve as
the discovery phase — not throwaway Python scripts.

**Rationale**: Solo developer with 48-72 hours. Building twice (prototype
then production) wastes 30%+ of available time. The requirements document
provides complete code templates — use them directly.

### II. Channel-Agnostic Core, Channel-Specific Edges

The AI agent, database layer, and business logic MUST be channel-agnostic.
Channel-specific behavior (formatting, API calls, webhook parsing) MUST
live exclusively in channel handler modules (`channels/`). Adding or
removing a channel MUST NOT require changes to the agent or database layer.

**Rationale**: The scoring rubric awards 10 points for cross-channel
continuity. A unified core with pluggable channel adapters ensures a
customer identified via email is the same customer on WhatsApp — without
duplicating logic.

### III. Test-Driven Development (NON-NEGOTIABLE)

TDD is mandatory. The Red-Green-Refactor cycle MUST be strictly enforced:
1. **RED**: Write a failing test that defines the expected behavior
2. **GREEN**: Write the minimum code to make the test pass
3. **REFACTOR**: Clean up the code while keeping tests green

Rules:
- Tests MUST be written BEFORE implementation code — no exceptions
- Tests MUST fail before implementation begins (proves the test is valid)
- Every function, endpoint, tool, and handler MUST have corresponding tests
- Minimum 80% code coverage gate — CI/build MUST fail below this threshold
- Test categories: unit (isolated logic), integration (component interaction),
  contract (API shape), E2E (full pipeline)
- Mock external dependencies (OpenAI API, Gmail, Twilio, Kafka) in unit tests
- Use real PostgreSQL (via testcontainers or docker) for integration tests

**Rationale**: A 24/7 AI agent handling real customer messages cannot ship
untested code. TDD catches regressions before they reach production, forces
clear interface design, and serves as living documentation. The 80% gate
ensures no component ships without verification.

### IV. Database as Source of Truth

All state MUST be persisted in PostgreSQL. No in-memory-only state for
conversations, tickets, customers, or message history. Every agent
interaction MUST create a ticket and store messages before responding.
The PostgreSQL schema IS the CRM — no external CRM integration required.

**Rationale**: 24/7 operation requires surviving pod restarts and scaling.
In-memory state dies with the process. The database ensures conversation
continuity across worker pods, channel switches, and infrastructure failures.

### V. Async Pipeline — Kafka Decouples Intake from Processing

Channel webhook handlers MUST publish to Kafka and return immediately.
Agent processing MUST happen in separate worker pods consuming from Kafka.
No channel handler should block on agent response generation.

**Rationale**: Webhook endpoints (Gmail Pub/Sub, Twilio) have timeout
constraints. Decoupling intake from processing enables independent scaling
of API pods (handle webhook volume) and worker pods (handle AI processing
load). Also provides a dead-letter queue for failed messages.

### VI. Fail Gracefully — Never Lose a Customer Message

Every processing error MUST result in: (a) an apologetic response sent to
the customer via their channel, (b) the original message published to a
dead-letter queue for human review, (c) structured error logging. Agent
failures MUST NOT surface raw errors to customers. Escalation to human
support is always the fallback.

**Rationale**: 24/7 readiness (10 points) requires resilience. A crashed
agent that silently drops messages is worse than one that says "I'm having
trouble, a human will follow up." Customer trust depends on reliability.

### VII. Secrets in Environment, Config in Code

API keys, credentials, and tokens MUST come from environment variables or
Kubernetes Secrets. NEVER hardcode secrets in source code, config files,
or Docker images. Non-secret configuration (response length limits, enabled
channels, log levels) MUST use ConfigMaps or environment variables with
sensible defaults.

**Rationale**: The project uses Gmail OAuth credentials, Twilio auth tokens,
OpenAI API keys, and database passwords. A single leaked credential
compromises the entire system. Environment-based config also enables
different settings per deployment environment.

### VIII. Smallest Viable Diff — Build Incrementally

Each development step MUST produce a working, testable increment. Commit
after each logical unit of work. Never attempt to build the entire system
in one pass. The build order MUST follow dependency chains:
Context → Database → Agent → Web Form → Kafka → Gmail → WhatsApp → K8s.

**Rationale**: Solo developer risk mitigation. If you run out of time at
any checkpoint, you have a demonstrable, working system. A complete
DB + Agent + Web Form scores 40+ points even without Gmail/WhatsApp/K8s.

## Technology Stack & Constraints

### Required Stack

| Layer | Technology | Version/Notes |
|-------|-----------|---------------|
| Language | Python | 3.11+ |
| AI Agent | OpenAI Agents SDK | `@function_tool` pattern |
| API Framework | FastAPI | Async, uvicorn |
| Database | PostgreSQL 16 | pgvector extension for semantic search |
| DB Driver | asyncpg | Async PostgreSQL access |
| Event Streaming | Apache Kafka | aiokafka producer/consumer |
| Frontend | React / Next.js | Web Support Form only |
| Email | Gmail API | OAuth2 + Pub/Sub push notifications |
| Messaging | Twilio WhatsApp API | Webhook + REST |
| Testing | pytest + pytest-asyncio | TDD mandatory, 80% coverage gate |
| Test Coverage | pytest-cov | Enforced in CI |
| Test HTTP | httpx + AsyncClient | FastAPI integration tests |
| Load Testing | Locust | 24/7 readiness validation |
| Container | Docker | Multi-stage builds |
| Orchestration | Kubernetes | minikube for local dev |

### Performance Budgets

- Agent response processing: < 3 seconds p95
- Webhook endpoint response: < 500ms (publish to Kafka and return)
- Message delivery: < 30 seconds end-to-end
- System uptime: > 99.9% over 24-hour test
- Cross-channel customer identification: > 95% accuracy
- Escalation rate: < 25%

### Hard Constraints

- Web Support Form is a REQUIRED deliverable (10 points)
- The agent MUST NEVER discuss pricing — escalate immediately
- The agent MUST NEVER promise features not in documentation
- The agent MUST NEVER process refunds — escalate to billing
- Tickets MUST be created BEFORE any agent response
- Responses MUST be formatted per channel (email: formal, WhatsApp: concise, web: semi-formal)
- Minimum 80% test coverage — no merge without passing this gate
- Tests MUST be written BEFORE implementation (Red-Green-Refactor)

## Development Workflow

### Build Order (Dependency Chain)

```
Step 1: Context files (company-profile, product-docs, sample-tickets)
Step 2: PostgreSQL schema + database queries layer
Step 3: OpenAI Agents SDK agent + tools
Step 4: Web Support Form (React) + FastAPI endpoints
Step 5: Kafka event streaming + unified message processor
Step 6: Gmail channel integration
Step 7: WhatsApp/Twilio channel integration
Step 8: Kubernetes deployment manifests
Step 9: E2E testing + documentation + discovery log
```

### Commit Discipline

- Commit after each completed step
- Commit messages: `feat:`, `fix:`, `infra:`, `docs:` prefixes
- Each commit MUST leave the system in a runnable state
- No "WIP" commits on the main feature branch

### Testing Strategy (TDD — Red-Green-Refactor)

For every feature, the workflow is:
1. Write failing tests (RED)
2. Implement minimum code to pass (GREEN)
3. Refactor while tests stay green (REFACTOR)

| Test Layer | Scope | Tools | When |
|------------|-------|-------|------|
| Unit | Isolated functions, tools, formatters | pytest, unittest.mock | Every function |
| Integration | DB queries, channel handlers, API endpoints | pytest-asyncio, httpx, testcontainers | Every component |
| Contract | API request/response shape validation | httpx + AsyncClient | Every endpoint |
| E2E | Full pipeline (form → Kafka → agent → response) | pytest + docker-compose | Per channel |
| Load | 24/7 readiness, concurrent users | Locust | Pre-deployment |

Coverage enforcement:
- `pytest --cov=src --cov-fail-under=80` MUST pass before any merge
- Mock external APIs (OpenAI, Gmail, Twilio) in unit/integration tests
- Use real PostgreSQL for integration tests (docker or testcontainers)
- Test each channel independently, then test cross-channel continuity

## Governance

This constitution defines the non-negotiable principles for the CRM
Digital FTE project. All implementation decisions MUST be validated against
these principles.

**Amendment procedure**: Any principle change MUST be documented with
rationale, the version MUST be incremented, and dependent templates MUST
be checked for consistency.

**Versioning policy**: MAJOR for principle removal/redefinition, MINOR for
new principles or material expansion, PATCH for clarifications.

**Compliance review**: Before each commit, verify the change does not
violate any Hard Constraint or Core Principle listed above.

**Version**: 1.1.0 | **Ratified**: 2026-02-08 | **Last Amended**: 2026-02-08
