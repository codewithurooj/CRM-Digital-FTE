# Tasks: Customer Success AI Agent (Digital FTE)

**Input**: Design documents from `/specs/002-customer-success-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Branch**: `002-customer-success-agent`
**TDD**: Mandatory — Red-Green-Refactor, 80% coverage gate

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- **[SKILL: x]** / **[AGENT: x]**: Skill or agent from `.claude/skill-registry.md`
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, context files, dependencies, configuration

- [ ] T001 Create production directory structure per plan.md — create all subdirectories: `production/{agent,channels,workers,api/endpoints,database/queries,database/migrations,schemas,tests/{unit,integration,contract,e2e,load},k8s}` and `web-form/src/{components,hooks,services}` [SKILL: fastapi-sqlmodel]
- [ ] T002 Initialize Python project — create `production/requirements.txt` (fastapi, uvicorn, asyncpg, aiokafka, openai-agents, google-api-python-client, twilio, pydantic-settings, python-dotenv) and `production/requirements-dev.txt` (pytest, pytest-asyncio, pytest-cov, httpx, locust) [SKILL: fastapi-sqlmodel]
- [ ] T003 [P] Create environment configuration in `production/config.py` — Pydantic Settings class with DATABASE_URL, KAFKA_BOOTSTRAP_SERVERS, OPENAI_API_KEY, GMAIL_*, TWILIO_*, LOG_LEVEL, ENABLED_CHANNELS, API_HOST, API_PORT. Use lazy init pattern. [SKILL: fastapi-sqlmodel]
  - **TDD**: Test config loads from env vars, defaults work, secrets not hardcoded → `production/tests/unit/test_config.py`
- [ ] T004 [P] Create `.env.example` in `production/.env.example` with all required env vars (no real values) [SKILL: fastapi-sqlmodel]
- [ ] T005 [P] Create context files — write `production/context/company-profile.md`, `production/context/product-docs.md`, `production/context/sample-tickets.json`, `production/context/escalation-rules.md`, `production/context/brand-voice.md` for fictional TechCorp SaaS company
  - **TDD**: Test files exist and are valid (JSON parseable, MD non-empty) → `production/tests/unit/test_context_files.py`
- [ ] T006 [P] Create test conftest with fixtures in `production/tests/conftest.py` — env var setup, mock factories for DB pool, Kafka producer, OpenAI client [AGENT: nl-test-generator]
- [ ] T007 [P] Initialize React/Next.js project in `web-form/` — `package.json` with React 18, Next.js, testing-library [SKILL: nextjs-betterauth]

**Checkpoint**: Project skeleton ready, `pip install -r requirements.txt` and `npm install` succeed

---

## Phase 2: Foundational — Database Layer (Blocking Prerequisites)

**Purpose**: PostgreSQL schema, asyncpg pool, CRUD queries for all 8 tables. MUST complete before any user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Schema & Pool

- [ ] T008 Write PostgreSQL DDL in `production/database/schema.sql` — all 8 tables (customers, customer_identifiers, conversations, messages, tickets, knowledge_base, channel_configs, agent_metrics) with extensions, indexes, triggers per data-model.md [AGENT: db-migrator]
  - **TDD**: Validate DDL is syntactically correct, all tables present → `production/tests/unit/test_schema_validation.py`
- [ ] T009 Write seed data in `production/database/seed.sql` — channel configs (email/whatsapp/web_form), sample knowledge base entries from context/product-docs.md [AGENT: db-migrator]
- [ ] T010 Create migration `production/database/migrations/001_initial_schema.sql` (copy of schema.sql, idempotent) [AGENT: db-migrator]
- [ ] T011 Implement asyncpg connection pool in `production/database/pool.py` — lazy singleton pattern, configurable min/max connections, health check method [SKILL: fastapi-sqlmodel]
  - **TDD**: Test pool creation, lazy init, health check returns bool → `production/tests/unit/test_database_pool.py`
- [ ] T012 Create `production/database/__init__.py` and `production/database/queries/__init__.py` with exports

### CRUD Query Modules (all [P] — different files)

- [ ] T013 [P] Implement customer queries in `production/database/queries/customers.py` — create_customer, get_customer_by_email, get_customer_by_id, update_customer, resolve_identity (cross-channel lookup via customer_identifiers) [AGENT: db-migrator]
  - **TDD**: Test each query function with mock pool → `production/tests/unit/test_queries_customers.py`
- [ ] T014 [P] Implement conversation queries in `production/database/queries/conversations.py` — create_conversation, get_conversation, update_status, close_conversation, get_active_by_customer [AGENT: db-migrator]
  - **TDD**: Test each query function → `production/tests/unit/test_queries_conversations.py`
- [ ] T015 [P] Implement message queries in `production/database/queries/messages.py` — store_message, get_messages_by_conversation, get_customer_history (cross-channel, ordered by created_at) [AGENT: db-migrator]
  - **TDD**: Test each query function → `production/tests/unit/test_queries_messages.py`
- [ ] T016 [P] Implement ticket queries in `production/database/queries/tickets.py` — create_ticket, get_ticket_by_number, update_ticket_status, get_tickets_by_customer [AGENT: db-migrator]
  - **TDD**: Test each query function → `production/tests/unit/test_queries_tickets.py`
- [ ] T017 [P] Implement knowledge base queries in `production/database/queries/knowledge_base.py` — search_by_embedding (pgvector cosine similarity, top 5), insert_entry, get_by_category [AGENT: db-migrator]
  - **TDD**: Test vector search query construction, result parsing → `production/tests/unit/test_queries_knowledge_base.py`
- [ ] T018 [P] Implement metrics queries in `production/database/queries/metrics.py` — record_metric, get_channel_metrics (aggregated per data-model.md query pattern), get_metrics_by_type [AGENT: db-migrator]
  - **TDD**: Test metric recording and aggregation → `production/tests/unit/test_queries_metrics.py`

### Pydantic Schemas (all [P] — different files)

- [ ] T019 [P] Create support form schemas in `production/schemas/support_form.py` — SupportFormRequest (name, email, subject, category enum, priority enum, message with validators), SupportFormResponse (ticket_id, status, message, created_at) per contracts/web-form.md [SKILL: fastapi-sqlmodel]
- [ ] T020 [P] Create message schemas in `production/schemas/messages.py` — InboundMessage (customer_identifier, identifier_type, channel, content, subject, metadata, timestamp), OutboundMessage [SKILL: fastapi-sqlmodel]
- [ ] T021 [P] Create ticket schemas in `production/schemas/tickets.py` — TicketResponse (ticket_id, status, category, priority, subject, source_channel, timestamps, responses[]) per contracts/tickets.md [SKILL: fastapi-sqlmodel]
- [ ] T022 [P] Create health schemas in `production/schemas/health.py` — HealthResponse (status, components{database,kafka,gmail,whatsapp,agent}, version, timestamp) per contracts/health.md [SKILL: fastapi-sqlmodel]
- [ ] T023 [P] Create metrics schemas in `production/schemas/metrics.py` — ChannelMetricsResponse (period, channels[], totals) per contracts/metrics.md [SKILL: fastapi-sqlmodel]

### FastAPI App Shell

- [ ] T024 Create FastAPI app factory in `production/api/main.py` — CORS, error handlers, lifespan (init DB pool + Kafka producer on startup, close on shutdown) [SKILL: fastapi-sqlmodel]
  - **TDD**: Test app creates, CORS headers present, lifespan hooks called → `production/tests/unit/test_app_factory.py`
- [ ] T025 Create shared dependencies in `production/api/dependencies.py` — get_db_pool, get_kafka_producer as FastAPI Depends() [SKILL: fastapi-sqlmodel]
- [ ] T026 Create route registration in `production/api/router.py` — include all endpoint routers under `/api/v1/` prefix [SKILL: fastapi-sqlmodel]
- [ ] T027 Create `production/api/__init__.py` and `production/api/endpoints/__init__.py`

### Docker Compose (Infrastructure)

- [ ] T028 Create `production/docker-compose.yml` — PostgreSQL 16 with pgvector, Kafka + Zookeeper, with health checks and volume mounts per quickstart.md [SKILL: dockerfile-generator]

**Checkpoint**: Foundation ready — DB pool connects, queries run, schemas validate, FastAPI starts. Run `pytest production/tests/unit/ -v` — all pass.

---

## Phase 3: User Story 1 — Web Support Form Submission (Priority: P1) 🎯 MVP

**Goal**: Customer submits web form → ticket created → confirmation returned → status checkable

**Independent Test**: Submit form via React component → verify ticket in DB → confirm response returned

**Scoring**: Web Support Form (10pts) + partial Database/Kafka (5pts)

### Tests for US1 (TDD — write first, must FAIL)

- [ ] T029 [P] [US1] Contract test for `POST /api/v1/support/form` in `production/tests/contract/test_web_form_contract.py` — validate request/response schema per contracts/web-form.md (201, 400, 503) [AGENT: nl-test-generator]
- [ ] T030 [P] [US1] Contract test for `GET /api/v1/tickets/{ticket_id}` in `production/tests/contract/test_ticket_contract.py` — validate response schema per contracts/tickets.md (200, 404) [AGENT: nl-test-generator]
- [ ] T031 [P] [US1] Integration test for web form submission flow in `production/tests/integration/test_support_form_api.py` — submit form → ticket created in DB → response has ticket_id [AGENT: nl-test-generator]
- [ ] T032 [P] [US1] React component test in `web-form/tests/SupportForm.test.jsx` — form renders, validates inputs, submits, shows loading, shows success [AGENT: nl-test-generator]

### Implementation for US1

- [ ] T033 [US1] Implement web form channel handler in `production/channels/web_form_handler.py` — parse form data to InboundMessage, format response per channel config (semi-formal, 300 words, ticket reference) [SKILL: fastapi-sqlmodel]
  - **TDD**: Test parse_inbound and format_response → `production/tests/unit/test_web_form_handler.py`
- [ ] T034 [US1] Implement `POST /api/v1/support/form` endpoint in `production/api/endpoints/support_form.py` — validate input, resolve/create customer, create ticket, store message, return ticket_id (< 500ms) [SKILL: fastapi-sqlmodel]
- [ ] T035 [US1] Implement `GET /api/v1/tickets/{ticket_id}` endpoint in `production/api/endpoints/tickets.py` — lookup ticket by TKT-XXXX number, return status + responses [SKILL: fastapi-sqlmodel]
- [ ] T036 [US1] Build React SupportForm component in `web-form/src/components/SupportForm.jsx` — fields: name, email, subject, category (dropdown), priority (dropdown), message (textarea). Client-side validation: name≥2, email valid, subject≥5, message≥10. Loading state, disable on submit. [SKILL: nextjs-betterauth]
- [ ] T037 [US1] Build FormField reusable component in `web-form/src/components/FormField.jsx` — input with label, error display, required indicator [SKILL: nextjs-betterauth]
- [ ] T038 [US1] Build SuccessMessage component in `web-form/src/components/SuccessMessage.jsx` — display ticket ID, next steps [SKILL: nextjs-betterauth]
- [ ] T039 [US1] Build StatusChecker component in `web-form/src/components/StatusChecker.jsx` — input for ticket ID, fetch status, display result [SKILL: nextjs-betterauth]
- [ ] T040 [US1] Create useFormValidation hook in `web-form/src/hooks/useFormValidation.js` — client-side validation rules matching server-side [SKILL: nextjs-betterauth]
- [ ] T041 [US1] Create API client service in `web-form/src/services/api.js` — submitForm(), getTicketStatus() with error handling [SKILL: nextjs-betterauth]
- [ ] T042 [US1] Create App.jsx entry in `web-form/src/App.jsx` — render SupportForm + StatusChecker [SKILL: nextjs-betterauth]

**Checkpoint**: Web form submits → ticket created → status checkable. Run contract + integration tests — all GREEN.

---

## Phase 4: User Story 2 — AI Agent Core (Priority: P1)

**Goal**: Agent receives message → creates ticket → searches knowledge base → generates response

**Independent Test**: Send question directly to agent → verify tool call order, KB search, ticket creation, response accuracy

**Scoring**: Agent Implementation (10pts)

### Tests for US2 (TDD)

- [ ] T043 [P] [US2] Unit test for agent tools in `production/tests/unit/test_agent_tools.py` — test each of 5 @function_tool definitions with mocked DB, verify return shapes [AGENT: nl-test-generator]
- [ ] T044 [P] [US2] Unit test for guardrails in `production/tests/unit/test_guardrails.py` — pricing/refund/legal/human-request triggers → escalation [AGENT: nl-test-generator]
- [ ] T045 [P] [US2] Unit test for response formatters in `production/tests/unit/test_formatters.py` — email (formal, ≤500 words), WhatsApp (conversational, ≤1600 chars), web (semi-formal, ≤300 words) [AGENT: nl-test-generator]
- [ ] T046 [P] [US2] Unit test for system prompts in `production/tests/unit/test_prompts.py` — prompt contains guardrail rules, tool order instructions, channel-aware formatting [AGENT: nl-test-generator]

### Implementation for US2

- [ ] T047 [US2] Create channel handler base class in `production/channels/base.py` — abstract ChannelHandler with parse_inbound(), format_response(), deliver() per research.md adapter pattern [SKILL: fastapi-sqlmodel]
- [ ] T048 [US2] Create system prompts in `production/agent/prompts.py` — system prompt enforcing tool order (create_ticket → get_history → search_kb → respond/escalate), guardrail rules (no pricing/refunds/false promises), channel formatting instructions [AGENT: agent-orchestrator]
- [ ] T049 [US2] Implement 5 @function_tool definitions in `production/agent/tools.py` — search_knowledge_base (pgvector query), create_ticket (DB insert), get_customer_history (cross-channel messages), escalate_to_human (update ticket status + reason), send_response (format + store) [AGENT: agent-orchestrator]
- [ ] T050 [US2] Implement response formatters in `production/agent/formatters.py` — format_for_email (formal, greeting+signature, ≤500 words), format_for_whatsapp (conversational, ≤1600 chars, split at sentence boundaries), format_for_web (semi-formal, ticket ref, ≤300 words) [AGENT: agent-orchestrator]
- [ ] T051 [US2] Implement agent runner in `production/agent/customer_success_agent.py` — OpenAI Agents SDK Agent definition, register 5 tools, run with conversation context, handle agent loop [AGENT: agent-orchestrator]
- [ ] T052 [US2] Create `production/agent/__init__.py` and `production/channels/__init__.py` with exports

**Checkpoint**: Agent processes a question → creates ticket → searches KB → returns formatted response. All unit tests GREEN.

---

## Phase 5: User Story 3 — Agent Guardrails and Escalation (Priority: P1)

**Goal**: Agent enforces hard constraints — pricing/refund/legal/human-request → immediate escalation

**Independent Test**: Send pricing/refund/legal queries → verify 100% escalation with correct reason codes

**Scoring**: Customer Experience (10pts — partial)

### Tests for US3 (TDD)

- [ ] T053 [P] [US3] Guardrail integration test in `production/tests/integration/test_guardrails_integration.py` — send pricing/refund/legal/human messages through agent, verify escalation in DB with reason codes [AGENT: nl-test-generator]

### Implementation for US3

- [ ] T054 [US3] Add guardrail keyword detection in `production/agent/tools.py` — escalate_to_human() checks for: pricing keywords, refund keywords, legal language ("lawyer","legal","sue","attorney"), explicit human requests ("human","agent","representative") [AGENT: agent-orchestrator]
- [ ] T055 [US3] Add sentiment-based escalation — if sentiment < 0.3, auto-escalate with reason "negative_sentiment" [AGENT: agent-orchestrator]
- [ ] T056 [US3] Add fallback escalation — if search_knowledge_base returns no results after 2 attempts, escalate with reason "no_kb_match" [AGENT: agent-orchestrator]
- [ ] T057 [US3] Implement graceful error responses — on any unrecoverable error, send apologetic message per channel format, never surface raw errors (FR-036, FR-037) [AGENT: agent-orchestrator]

**Checkpoint**: Guardrails enforced 100%. Pricing → escalated. Refund → escalated. Legal → escalated. Human request → escalated. Low sentiment → escalated.

---

## Phase 6: User Story 4 — Cross-Channel Customer Identity (Priority: P1)

**Goal**: Same customer recognized across email, WhatsApp, web form via unified identity resolution

**Independent Test**: Create customer via web form → submit via different channel with same email → verify single customer record

**Scoring**: Cross-Channel (10pts)

### Tests for US4 (TDD)

- [ ] T058 [P] [US4] Unit test for identity resolution in `production/tests/unit/test_identity_resolution.py` — resolve by email, resolve by phone, create new, merge identifiers [AGENT: nl-test-generator]
- [ ] T059 [P] [US4] Integration test for cross-channel identity in `production/tests/integration/test_cross_channel_identity.py` — web form then email same customer → single record [AGENT: nl-test-generator]

### Implementation for US4

- [ ] T060 [US4] Implement identity resolution service in `production/database/queries/customers.py` — resolve_customer_identity(identifier_value, identifier_type, channel) → find existing or create new, link identifiers [AGENT: db-migrator]
- [ ] T061 [US4] Add customer_identifiers management — create_identifier, link phone to existing email-based customer, prevent duplicates [AGENT: db-migrator]
- [ ] T062 [US4] Implement cross-channel history retrieval in `production/database/queries/messages.py` — get_full_customer_history(customer_id) returns messages from ALL channels chronologically [AGENT: db-migrator]

**Checkpoint**: Customer contacts via web form and email → recognized as same person → full history available across channels.

---

## Phase 7: User Story 5 — Channel-Appropriate Response Formatting (Priority: P2)

**Goal**: Same question → different response format per channel (email=formal, WhatsApp=concise, web=semi-formal)

**Independent Test**: Send "How do I reset my password?" via each channel → verify format/length/tone differences

**Scoring**: Customer Experience (10pts — additional)

### Tests for US5 (TDD)

- [ ] T063 [P] [US5] Unit test for channel formatting in `production/tests/unit/test_channel_formatting.py` — same content formatted differently per channel, WhatsApp splitting at sentence boundaries [AGENT: nl-test-generator]

### Implementation for US5

- [ ] T064 [US5] Implement email formatter in `production/channels/gmail_handler.py` — formal greeting ("Dear Customer"), detailed body, professional signature with ticket ref, ≤500 words [SKILL: fastapi-sqlmodel]
- [ ] T065 [US5] Implement WhatsApp formatter in `production/channels/whatsapp_handler.py` — conversational tone, ≤300 chars preferred, split at 1600 chars on sentence boundaries [SKILL: fastapi-sqlmodel]
- [ ] T066 [US5] Integrate channel configs from DB — load max_response_length, tone, response_template from channel_configs table per seed data [SKILL: fastapi-sqlmodel]

**Checkpoint**: Email responses are formal with signature. WhatsApp responses are short and conversational. Web responses are semi-formal with ticket reference.

---

## Phase 8: User Story 6 — Kafka Async Pipeline (Priority: P2)

**Goal**: Webhooks publish to Kafka → workers consume → agent processes → response routed back

**Independent Test**: Publish message to Kafka topic → verify worker consumes, agent processes, outbound response produced

**Scoring**: Database + Kafka (5pts) + 24/7 Readiness (10pts — partial)

### Tests for US6 (TDD)

- [ ] T067 [P] [US6] Unit test for Kafka client in `production/tests/unit/test_kafka_client.py` — producer sends, consumer receives, DLQ publish on error [AGENT: nl-test-generator]
- [ ] T068 [P] [US6] Integration test for Kafka pipeline in `production/tests/integration/test_kafka_pipeline.py` — publish inbound → worker consumes → agent runs → outbound produced [AGENT: nl-test-generator]

### Implementation for US6

- [ ] T069 [US6] Implement Kafka producer/consumer factory in `production/kafka_client.py` — lazy singleton, aiokafka, topics: fte.tickets.incoming, fte.tickets.outgoing, fte.tickets.dlq, partition by customer_id [AGENT: microservice-scaffolder]
  - **TDD**: Test producer creates, consumer subscribes, topic names correct → `production/tests/unit/test_kafka_client.py`
- [ ] T070 [US6] Implement message processor worker in `production/workers/message_processor.py` — consume from fte.tickets.incoming, resolve identity, create/resume conversation, run agent, store response, route to outbound topic, commit offset. On error: send apologetic msg, publish to DLQ, log [AGENT: microservice-scaffolder]
  - **TDD**: Test worker processes message, handles errors gracefully → `production/tests/unit/test_message_processor.py`
- [ ] T071 [US6] Update web form endpoint `production/api/endpoints/support_form.py` — after creating ticket, publish normalized InboundMessage to Kafka fte.tickets.incoming (return ticket_id within 500ms) [SKILL: fastapi-sqlmodel]
- [ ] T072 [US6] Create `production/workers/__init__.py` with exports

**Checkpoint**: Web form submission → Kafka → worker → agent → response stored. Message flow is async and decoupled.

---

## Phase 9: User Story 7 — Gmail Email Integration (Priority: P2)

**Goal**: Customer emails support@techcorp.com → Gmail Pub/Sub → webhook → Kafka → agent → reply in same thread

**Independent Test**: Simulate Gmail Pub/Sub notification → verify message parsed, published to Kafka, reply email constructed

**Scoring**: Channel Integrations (10pts — partial)

### Tests for US7 (TDD)

- [ ] T073 [P] [US7] Contract test for `POST /api/v1/webhooks/gmail` in `production/tests/contract/test_gmail_webhook_contract.py` — validate Pub/Sub payload shape, response 200, auth check 401 [AGENT: nl-test-generator]
- [ ] T074 [P] [US7] Integration test for Gmail flow in `production/tests/integration/test_gmail_integration.py` — simulate Pub/Sub → parse email → publish to Kafka [AGENT: nl-test-generator]

### Implementation for US7

- [ ] T075 [US7] Implement Gmail channel handler in `production/channels/gmail_handler.py` — parse_inbound (decode Pub/Sub base64, extract sender/subject/body), format_response (formal with greeting+signature), deliver (Gmail API reply in same thread) [SKILL: fastapi-sqlmodel]
  - **TDD**: Test parse and format with sample payloads → `production/tests/unit/test_gmail_handler.py`
- [ ] T076 [US7] Implement Gmail webhook endpoint in `production/api/endpoints/gmail_webhook.py` — validate Pub/Sub auth, decode payload, normalize to InboundMessage, publish to Kafka, return 200 [SKILL: fastapi-sqlmodel]
- [ ] T077 [US7] Add Gmail API client for sending replies — OAuth2 credentials from env, reply in thread using threadId from inbound metadata [SKILL: fastapi-sqlmodel]

**Checkpoint**: Gmail Pub/Sub notification → webhook → Kafka → agent → reply email in same thread.

---

## Phase 10: User Story 8 — WhatsApp Integration via Twilio (Priority: P2)

**Goal**: Customer sends WhatsApp → Twilio webhook → validate signature → Kafka → agent → Twilio reply

**Independent Test**: Simulate Twilio webhook POST → verify signature validated, message parsed, published to Kafka

**Scoring**: Channel Integrations (10pts — additional)

### Tests for US8 (TDD)

- [ ] T078 [P] [US8] Contract test for `POST /api/v1/webhooks/whatsapp` in `production/tests/contract/test_whatsapp_webhook_contract.py` — validate form-encoded payload, TwiML response, signature check 403 [AGENT: nl-test-generator]
- [ ] T079 [P] [US8] Integration test for WhatsApp flow in `production/tests/integration/test_whatsapp_integration.py` — simulate Twilio webhook → parse → Kafka [AGENT: nl-test-generator]

### Implementation for US8

- [ ] T080 [US8] Implement WhatsApp channel handler in `production/channels/whatsapp_handler.py` — parse_inbound (extract From/Body from form-encoded), format_response (conversational, split at 1600 chars), deliver (Twilio WhatsApp API) [SKILL: fastapi-sqlmodel]
  - **TDD**: Test parse, format, and message splitting → `production/tests/unit/test_whatsapp_handler.py`
- [ ] T081 [US8] Implement WhatsApp webhook endpoint in `production/api/endpoints/whatsapp_webhook.py` — validate X-Twilio-Signature, parse form-encoded body, normalize to InboundMessage, publish to Kafka, return TwiML `<Response/>` [SKILL: fastapi-sqlmodel]
- [ ] T082 [US8] Add Twilio signature validation utility — verify HMAC using TWILIO_AUTH_TOKEN from env [SKILL: fastapi-sqlmodel]

**Checkpoint**: Twilio webhook → validated → Kafka → agent → WhatsApp reply. Invalid signature → 403.

---

## Phase 11: User Story 9 — Kubernetes Deployment (Priority: P2)

**Goal**: Full system on K8s with auto-scaling, health probes, graceful restarts, secret management

**Independent Test**: Deploy to minikube → kill pods → verify recovery → check health endpoint

**Scoring**: Kubernetes (5pts) + 24/7 Readiness (10pts)

### Tests for US9 (TDD)

- [ ] T083 [P] [US9] Contract test for `GET /api/v1/health` in `production/tests/contract/test_health_contract.py` — validate response schema (status, components, version, timestamp) [AGENT: nl-test-generator]
- [ ] T084 [P] [US9] Integration test for health endpoint in `production/tests/integration/test_health_api.py` — healthy returns 200, degraded returns 200, unhealthy returns 503 [AGENT: nl-test-generator]

### Implementation for US9

- [ ] T085 [US9] Implement health endpoint in `production/api/endpoints/health.py` — check DB pool, Kafka connectivity, return component status per contracts/health.md [SKILL: fastapi-sqlmodel]
- [ ] T086 [US9] Create multi-stage Dockerfile in `production/Dockerfile` — Python 3.11-slim, copy requirements, install deps, copy code, uvicorn CMD [SKILL: dockerfile-generator]
- [ ] T087 [P] [US9] Create K8s namespace manifest in `production/k8s/namespace.yaml` — `crm-digital-fte` namespace [SKILL: helm-chart-builder]
- [ ] T088 [P] [US9] Create K8s secrets manifest in `production/k8s/secrets.yaml` — OPENAI_API_KEY, GMAIL_*, TWILIO_*, DATABASE_URL (base64 placeholders) [SKILL: helm-chart-builder]
- [ ] T089 [P] [US9] Create K8s configmap in `production/k8s/configmap.yaml` — LOG_LEVEL, ENABLED_CHANNELS, ESCALATION_THRESHOLDS [SKILL: helm-chart-builder]
- [ ] T090 [US9] Create PostgreSQL StatefulSet in `production/k8s/postgres-deployment.yaml` — PostgreSQL 16 + pgvector, PVC 10Gi, port 5432, liveness probe [SKILL: helm-chart-builder]
- [ ] T091 [US9] Create Kafka StatefulSet in `production/k8s/kafka-deployment.yaml` — Kafka + Zookeeper, PVC 5Gi, port 9092 [SKILL: helm-chart-builder]
- [ ] T092 [US9] Create API Deployment in `production/k8s/api-deployment.yaml` — 3 replicas, liveness/readiness probes on /api/v1/health, resource limits, env from secrets+configmap [SKILL: helm-chart-builder]
- [ ] T093 [US9] Create Worker Deployment in `production/k8s/worker-deployment.yaml` — 3 replicas, Kafka consumer health probe, resource limits [SKILL: helm-chart-builder]
- [ ] T094 [US9] Create HPA for API in `production/k8s/api-hpa.yaml` — min 3, max 20, target CPU 70% [SKILL: helm-chart-builder]
- [ ] T095 [US9] Create HPA for Workers in `production/k8s/worker-hpa.yaml` — min 3, max 30, target CPU 70% [SKILL: helm-chart-builder]
- [ ] T096 [US9] Create K8s Services — `production/k8s/api-service.yaml` (ClusterIP, 80→8000), `production/k8s/postgres-service.yaml` (ClusterIP, 5432) [SKILL: helm-chart-builder]

**Checkpoint**: `kubectl apply -f k8s/` succeeds on minikube. Pods start, health checks pass, HPA configured.

---

## Phase 12: User Story 10 — Monitoring and Channel Metrics (Priority: P3)

**Goal**: Per-channel metrics endpoint, alert thresholds, performance tracking

**Independent Test**: Process messages through each channel → query `/metrics/channels` → verify accurate per-channel breakdowns

**Scoring**: Monitoring (5pts)

### Tests for US10 (TDD)

- [ ] T097 [P] [US10] Contract test for `GET /api/v1/metrics/channels` in `production/tests/contract/test_metrics_contract.py` — validate response schema per contracts/metrics.md [AGENT: nl-test-generator]
- [ ] T098 [P] [US10] Integration test for metrics in `production/tests/integration/test_metrics_api.py` — record metrics → query → verify aggregation [AGENT: nl-test-generator]

### Implementation for US10

- [ ] T099 [US10] Implement metrics endpoint in `production/api/endpoints/metrics.py` — query per-channel aggregations (conversation count, avg sentiment, escalation count/rate, avg latency, message volume) for configurable period per contracts/metrics.md [SKILL: fastapi-sqlmodel]
- [ ] T100 [US10] Implement metrics collector worker in `production/workers/metrics_collector.py` — aggregate metrics periodically, check alert thresholds (latency > 3s, escalation rate > 25%), publish alerts [AGENT: microservice-scaffolder]
- [ ] T101 [US10] Add metric recording to agent tools — record response_latency, escalation, sentiment, tool_call, conversation_count, message_volume after each agent interaction in `production/agent/tools.py` [AGENT: agent-orchestrator]

**Checkpoint**: `/metrics/channels` returns accurate per-channel data. Alert thresholds configured.

---

## Phase 13: User Story 11 — Incubation Discovery and MCP Server (Priority: P2)

**Goal**: Discovery log documenting patterns, MCP server with 5 tools, transition documentation

**Independent Test**: MCP server exposes all 5 tools, discovery log has 10+ patterns documented

**Scoring**: Incubation Quality (10pts)

### Implementation for US11

- [ ] T102 [US11] Create discovery log in `specs/discovery-log.md` — analyze sample-tickets.json, document 10+ patterns per channel (email length, WhatsApp casualness, web form structure, common categories, sentiment patterns, escalation triggers) [SKILL: spec-writer]
- [ ] T103 [US11] Build MCP server with 5 tools — search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, send_response as MCP tool definitions with schemas [SKILL: mcp-server-creator]
- [ ] T104 [US11] Document MCP-to-function_tool transition — map each MCP tool to its OpenAI @function_tool counterpart, document added validation/error handling/DB integration [SKILL: spec-writer]

**Checkpoint**: Discovery log complete with 10+ patterns. MCP server responds to all 5 tools.

---

## Phase 14: User Story 12 — Innovation: Sentiment-Aware Routing (Priority: P3)

**Goal**: Sentiment analysis on every message, intelligent routing, learning from resolutions, daily digest

**Independent Test**: Send negative-sentiment messages → verify earlier escalation and priority bumps

**Scoring**: Innovation (10pts)

### Implementation for US12

- [ ] T105 [US12] Add real-time sentiment scoring to message processing in `production/workers/message_processor.py` — score every inbound message, store in conversation.sentiment_score, track trend [AGENT: agent-orchestrator]
- [ ] T106 [US12] Implement sentiment-based priority routing — conversations with sentiment < 0.3 auto-escalate, sentiment 0.3-0.5 bump priority to "high" [AGENT: agent-orchestrator]
- [ ] T107 [US12] Implement daily digest generator — summarize top issues, average sentiment, resolution rates, response times per channel. Store as agent_metric or expose via API [AGENT: agent-orchestrator]
- [ ] T108 [US12] Implement learning pipeline — analyze resolved tickets for novel solutions, flag candidates for knowledge base updates [AGENT: agent-orchestrator]

**Checkpoint**: Negative sentiment → earlier escalation. Daily digest summarizes per-channel stats.

---

## Phase 15: Polish & Cross-Cutting Concerns

**Purpose**: E2E tests, load tests, documentation, security hardening

### E2E Tests

- [ ] T109 [P] E2E test for web form flow in `production/tests/e2e/test_web_form_e2e.py` — form submit → Kafka → agent → response stored → ticket queryable [AGENT: testing-agent]
- [ ] T110 [P] E2E test for Gmail flow in `production/tests/e2e/test_gmail_e2e.py` — Pub/Sub notification → Kafka → agent → email reply [AGENT: testing-agent]
- [ ] T111 [P] E2E test for WhatsApp flow in `production/tests/e2e/test_whatsapp_e2e.py` — Twilio webhook → Kafka → agent → WhatsApp reply [AGENT: testing-agent]
- [ ] T112 E2E test for cross-channel flow in `production/tests/e2e/test_cross_channel.py` — customer contacts via web form then email → single record, full history [AGENT: testing-agent]

### Load Tests

- [ ] T113 Create Locust load test in `production/tests/load/locustfile.py` — simulate 100+ web forms, 50+ emails, 50+ WhatsApp messages over test period, verify no message loss [AGENT: testing-agent]

### Documentation

- [ ] T114 [P] Create deployment guide in `production/docs/deployment-guide.md` — step-by-step K8s deployment, Docker Compose, env setup [SKILL: spec-writer]
- [ ] T115 [P] Create API reference in `production/docs/api-reference.md` — all endpoints, schemas, examples [SKILL: stateless-api-designer]

### Security & Hardening

- [ ] T116 Security audit — verify no hardcoded secrets, SQL parameterized (asyncpg $1), input validation on all endpoints, Twilio signature check, Gmail auth check [AGENT: testing-agent]
- [ ] T117 Edge case handling — empty messages, media attachments (acknowledge text-only), Kafka unavailable (retry+backoff), OpenAI unavailable (fallback msg), malformed payloads (400), rapid WhatsApp messages (batch) [SKILL: fastapi-sqlmodel]

### Coverage Gate

- [ ] T118 Run full test suite with coverage — `pytest --cov=production --cov-fail-under=80 -v` — all tests pass, ≥80% coverage [AGENT: testing-agent]

**Checkpoint**: All tests GREEN, 80%+ coverage, documentation complete, security verified.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──→ Phase 2 (Foundational/DB) ──→ Phase 3+ (User Stories)
                                                        │
                    ┌───────────────────────────────────┤
                    │             │            │         │
                Phase 3 (US1)  Phase 4 (US2)  Phase 5 (US3)  Phase 6 (US4)
                Web Form       Agent Core    Guardrails      Cross-Channel
                    │             │            │         │
                    └─────────────┴────────────┴─────────┘
                                  │
                    ┌─────────────┼─────────────────────┐
                    │             │            │         │
                Phase 7 (US5)  Phase 8 (US6)  Phase 9 (US7)  Phase 10 (US8)
                Formatting     Kafka          Gmail          WhatsApp
                    │             │            │         │
                    └─────────────┴────────────┴─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │              │
                Phase 11 (US9)  Phase 12 (US10) Phase 13 (US11)
                K8s Deploy      Metrics         Incubation
                    │             │              │
                    └─────────────┴──────────────┘
                                  │
                             Phase 14 (US12)
                             Innovation
                                  │
                             Phase 15
                             Polish
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|-----------|-------------------|
| US1 (Web Form) | Phase 2 only | US2, US3, US4 |
| US2 (Agent Core) | Phase 2 only | US1, US3, US4 |
| US3 (Guardrails) | US2 (agent exists) | US1, US4 |
| US4 (Cross-Channel) | Phase 2 only | US1, US2, US3 |
| US5 (Formatting) | US2 (formatters exist) | US6, US7, US8 |
| US6 (Kafka) | US1, US2 (form + agent exist) | US5 |
| US7 (Gmail) | US2, US6 (agent + Kafka exist) | US8 |
| US8 (WhatsApp) | US2, US6 (agent + Kafka exist) | US7 |
| US9 (K8s) | US1-US8 (all components ready) | US10, US11 |
| US10 (Metrics) | US2, Phase 2 (agent + DB) | US9, US11 |
| US11 (Incubation) | Context files only | US9, US10 |
| US12 (Innovation) | US2, US10 (agent + metrics) | — |

### Within Each Story

1. Tests written FIRST → must FAIL (RED)
2. Models/schemas before services
3. Services before endpoints
4. Core implementation before integration
5. Story complete and GREEN before moving to next

### Parallel Opportunities per Phase

```bash
# Phase 2 — all query modules in parallel:
T013, T014, T015, T016, T017, T018  # different files
T019, T020, T021, T022, T023        # different schema files

# Phase 3 (US1) — tests in parallel, then React components in parallel:
T029, T030, T031, T032              # different test files
T036, T037, T038, T039, T040, T041  # different component files

# Phase 4 (US2) — tests in parallel:
T043, T044, T045, T046              # different test files

# Phase 11 (US9) — K8s manifests in parallel:
T087, T088, T089                    # namespace, secrets, configmap
T094, T095                          # HPAs
```

---

## Implementation Strategy

### MVP First (Phases 1-4 = US1 + US2)

1. Complete Phase 1: Setup → skeleton ready
2. Complete Phase 2: Foundational → DB + schemas + app shell ready
3. Complete Phase 3: US1 → Web form works end-to-end
4. Complete Phase 4: US2 → Agent processes questions
5. **STOP and VALIDATE**: Form submits, agent responds, ticket created
6. This covers 30+ points: Web Form (10) + Agent (10) + partial DB (5) + partial CX (10)

### Incremental Delivery (Phases 5-15)

7. Phase 5: US3 → Guardrails enforced
8. Phase 6: US4 → Cross-channel identity works
9. Phase 7: US5 → Responses properly formatted
10. Phase 8: US6 → Kafka pipeline live (async processing)
11. Phase 9-10: US7+US8 → Gmail + WhatsApp channels live
12. Phase 11: US9 → K8s deployment
13. Phase 12: US10 → Monitoring active
14. Phase 13: US11 → Incubation deliverables
15. Phase 14: US12 → Innovation features
16. Phase 15: Polish → full test suite, docs, security

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 118 |
| **Phase 1 (Setup)** | 7 tasks |
| **Phase 2 (Foundational)** | 21 tasks |
| **US1 (Web Form)** | 14 tasks |
| **US2 (Agent Core)** | 10 tasks |
| **US3 (Guardrails)** | 5 tasks |
| **US4 (Cross-Channel)** | 5 tasks |
| **US5 (Formatting)** | 4 tasks |
| **US6 (Kafka)** | 6 tasks |
| **US7 (Gmail)** | 5 tasks |
| **US8 (WhatsApp)** | 5 tasks |
| **US9 (K8s)** | 14 tasks |
| **US10 (Metrics)** | 5 tasks |
| **US11 (Incubation)** | 3 tasks |
| **US12 (Innovation)** | 4 tasks |
| **Polish** | 10 tasks |
| **Scoring Coverage** | All 10 categories covered |
| **Parallel Opportunities** | 30+ tasks marked [P] |
| **MVP Scope** | Phases 1-4 (52 tasks) |

### Scoring Category Coverage

| Category (Points) | Covered By |
|-------------------|-----------|
| Incubation Quality (10) | Phase 13 — US11: T102-T104 |
| Agent Implementation (10) | Phase 4 — US2: T047-T052 |
| Web Support Form (10) | Phase 3 — US1: T033-T042 |
| Channel Integrations (10) | Phase 9 — US7: T075-T077, Phase 10 — US8: T080-T082 |
| Database + Kafka (5) | Phase 2: T008-T018, Phase 8 — US6: T069-T072 |
| Kubernetes (5) | Phase 11 — US9: T086-T096 |
| 24/7 Readiness (10) | Phase 11 — US9: T092-T096 (HPA, probes, restarts) |
| Cross-Channel (10) | Phase 6 — US4: T058-T062 |
| Monitoring (5) | Phase 12 — US10: T097-T101 |
| Customer Experience (10) | Phase 5 — US3: T053-T057, Phase 7 — US5: T063-T066 |
| Documentation (5) | Phase 15: T114-T115 |
| Innovation (10) | Phase 14 — US12: T105-T108 |
