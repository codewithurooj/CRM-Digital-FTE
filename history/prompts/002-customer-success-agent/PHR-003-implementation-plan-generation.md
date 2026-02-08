---
id: PHR-003
title: implementation-plan-generation
stage: plan
date: 2026-02-08
surface: cli
model: claude-opus-4-6
feature: 002-customer-success-agent
branch: 002-customer-success-agent
user: architect
command: /sp.plan
labels: [plan, architecture, research, data-model, contracts]
links:
  spec: specs/002-customer-success-agent/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - specs/002-customer-success-agent/plan.md
  - specs/002-customer-success-agent/research.md
  - specs/002-customer-success-agent/data-model.md
  - specs/002-customer-success-agent/quickstart.md
  - specs/002-customer-success-agent/contracts/web-form.md
  - specs/002-customer-success-agent/contracts/gmail-webhook.md
  - specs/002-customer-success-agent/contracts/whatsapp-webhook.md
  - specs/002-customer-success-agent/contracts/health.md
  - specs/002-customer-success-agent/contracts/metrics.md
  - specs/002-customer-success-agent/contracts/tickets.md
tests:
  - none (planning phase — no implementation yet)
---

## Prompt

Create the implementation plan for CRM Digital FTE. Read the spec at specs/crm-digital-fte/spec.md and the constitution at .specify/memory/constitution.md. Generate artifacts: plan.md (architecture, component diagram, data flow), research.md (tech stack rationale), data-model.md (full PostgreSQL schema for 8 CRM tables with pgvector), and contracts/ (API contracts for all endpoints). Reference the build order from constitution.

## Response snapshot

Generated 10 artifacts for the CRM Digital FTE implementation plan:

1. **plan.md** — Full architecture plan with: technical context, constitution check (8/8 PASS), project structure (production/ + web-form/), high-level data flow diagram (webhooks → Kafka → worker → agent → response), cross-channel identity resolution flow, agent tool execution order, guardrail check flow, Kafka topic design (3 topics), K8s deployment architecture, 9-step build order, key design decisions (asyncpg, unified message format, lazy init, channel adapter interface, ticket number generation), NFRs table, and risk analysis (3 risks).

2. **research.md** — 10 technology decisions with Decision/Rationale/Alternatives format: asyncpg over SQLAlchemy, aiokafka over confluent-kafka, OpenAI Agents SDK @function_tool, pgvector over dedicated vector DB, FastAPI, React/Next.js, Kubernetes/minikube, pytest ecosystem, channel adapter pattern, Kafka topic design.

3. **data-model.md** — Full PostgreSQL DDL for 8 tables (customers, customer_identifiers, conversations, messages, tickets, knowledge_base, channel_configs, agent_metrics) with CHECK constraints, indexes (including HNSW for pgvector), auto-generated TKT-XXXX ticket numbers via sequence+trigger, updated_at triggers, seed data for channel configs, and key query patterns.

4. **contracts/** — 6 API contracts: web-form POST, gmail-webhook POST, whatsapp-webhook POST, health GET, metrics GET, tickets GET — each with request/response schemas, validation rules, error responses, and implementation notes.

5. **quickstart.md** — Local development setup guide.

## Outcome

- ✅ Impact: All Phase 0 and Phase 1 planning artifacts generated. Constitution check passed 8/8. Ready for /sp.tasks to generate Phase 2 task breakdown.
- 🧪 Tests: N/A (planning phase)
- 📁 Files: 10 files created in specs/002-customer-success-agent/
- 🔁 Next prompts: Run `/sp.tasks` to generate tasks.md from the plan, then `/sp.implement` to begin TDD implementation starting with Step 1 (context files) and Step 2 (database schema).
- 🧠 Reflection: Background agents failed to write files due to permission constraints in subprocesses. Direct writes from main context succeeded. Future plans should write files directly rather than delegating file writes to background agents.

## Evaluation notes (flywheel)

- Failure modes observed: Background Task agents had tool permissions auto-denied, unable to write files. Required fallback to direct writes from main context.
- Graders run and results (PASS/FAIL): Constitution check PASS (8/8 principles). All artifacts generated PASS.
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Write files directly instead of using background agents for file creation tasks.
