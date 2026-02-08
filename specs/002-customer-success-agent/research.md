# Research: Technology Decisions — CRM Digital FTE

**Branch**: `002-customer-success-agent` | **Date**: 2026-02-08
**Purpose**: Resolve all technical unknowns and document technology choices with rationale.

## 1. Database Driver: asyncpg (over SQLAlchemy)

**Decision**: Use asyncpg as the primary PostgreSQL driver with hand-written SQL queries. No ORM.

**Rationale**:
- **Performance**: asyncpg is 2-3x faster than SQLAlchemy async for simple CRUD operations. Benchmarks consistently show asyncpg as the fastest Python PostgreSQL driver.
- **Schema-first approach**: The CRM schema is stable (8 tables, defined upfront in DDL). An ORM adds abstraction overhead with no benefit when the schema doesn't change frequently.
- **pgvector compatibility**: Vector similarity queries (`SELECT ... ORDER BY embedding <=> $1 LIMIT 5`) are simpler and more predictable in raw SQL than through ORM abstractions.
- **Async-native**: asyncpg is built from the ground up for asyncio, matching FastAPI's async model perfectly.
- **Connection pooling**: Built-in connection pool with configurable min/max connections.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| SQLAlchemy async (with asyncpg backend) | ORM overhead for simple CRM queries. Adds complexity without proportional benefit for a stable schema. |
| psycopg3 (async mode) | Newer, less battle-tested than asyncpg. Smaller community and fewer production references. |
| databases library | Abstracts too much, limited pgvector support, smaller ecosystem. |

---

## 2. Event Streaming: aiokafka (over confluent-kafka)

**Decision**: Use aiokafka for Kafka producer and consumer operations.

**Rationale**:
- **Native asyncio**: aiokafka integrates naturally with FastAPI's async event loop. No need for threading or executor workarounds.
- **Simple API**: The produce/consume pattern for this project is straightforward — publish normalized messages, consume and process. aiokafka's API is clean for this use case.
- **No C dependency**: Pure Python implementation means simpler Docker builds (no librdkafka compilation step) and easier CI/CD.
- **Sufficient throughput**: The system handles hundreds of messages per day, not millions. aiokafka's performance is more than adequate.
- **Consumer group support**: Built-in support for consumer groups, which enables multiple worker pods to share the load.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| confluent-kafka-python | C extension (librdkafka) adds build complexity. Sync-first API requires threading with asyncio. Overkill for this volume. |
| kafka-python | Pure Python but synchronous. Would require threading alongside asyncio, adding complexity. |
| faust | Full stream processing framework. Massive overkill for a simple produce/consume pattern. |

---

## 3. AI Agent Framework: OpenAI Agents SDK with @function_tool

**Decision**: Use the OpenAI Agents SDK with `@function_tool` decorated functions for the 5 agent tools.

**Rationale**:
- **First-party SDK**: Maintained by OpenAI, designed specifically for tool-calling agents with GPT-4o.
- **Type-safe tools**: `@function_tool` decorator automatically generates JSON Schema from Python type hints, reducing boilerplate and preventing schema drift.
- **Built-in agent loop**: The SDK handles the tool execution loop (call model → execute tool → feed result back → repeat) without manual orchestration.
- **Conversation management**: Built-in conversation state management, reducing custom code for multi-turn interactions.
- **GPT-4o integration**: Optimized for GPT-4o's tool-calling capabilities, including parallel tool calls and structured outputs.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| LangChain | Heavy abstraction layer with many dependencies. More complexity than needed for a single-agent system. Chain/graph concepts add cognitive overhead. |
| Raw OpenAI API (chat completions) | No agent loop — would require manual tool dispatch, retry logic, and conversation management. Significant boilerplate. |
| AutoGen | Designed for multi-agent conversations. Overkill for a single customer success agent. |
| CrewAI | Same multi-agent focus as AutoGen. Unnecessary complexity for one agent with 5 tools. |

---

## 4. Vector Search: pgvector (over dedicated vector DB)

**Decision**: Use the pgvector extension in PostgreSQL 16 for knowledge base semantic search.

**Rationale**:
- **Single database**: All CRM data and vector search in one PostgreSQL instance. No additional infrastructure to deploy, monitor, or maintain.
- **HNSW index**: pgvector supports HNSW (Hierarchical Navigable Small World) indexes for fast approximate nearest neighbor search. Performance is excellent for the knowledge base size (~100-500 entries).
- **1536-dimensional vectors**: Compatible with OpenAI's text-embedding-3-small model output (1536 dimensions).
- **Transactional consistency**: Vector search results are transactionally consistent with the rest of the CRM data. No eventual consistency issues between the vector DB and the relational DB.
- **Operational simplicity**: One database to backup, one to monitor, one connection pool. Critical for a solo developer managing a 24/7 system.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| Pinecone | Managed service adds external dependency, network latency, and cost. Overkill for ~500 knowledge base entries. |
| Qdrant | Separate service to deploy and manage on K8s. Adds operational overhead for minimal benefit at this scale. |
| Weaviate | Same operational overhead as Qdrant. Full-featured but unnecessary for simple similarity search. |
| ChromaDB | Embedded mode doesn't survive pod restarts well. Not designed for production K8s deployment. |

---

## 5. API Framework: FastAPI + uvicorn

**Decision**: FastAPI with uvicorn as the ASGI server.

**Rationale**:
- **Async-native**: Built on Starlette with native async/await support, matching the async database and Kafka clients.
- **Automatic OpenAPI docs**: Generates Swagger UI and ReDoc documentation from Pydantic models and type hints. Reduces documentation effort.
- **Pydantic validation**: Request/response validation through Pydantic models. Type-safe, automatic error responses for invalid input.
- **High performance**: One of the fastest Python web frameworks. uvicorn with multiple workers handles the webhook volume easily.
- **Dependency injection**: FastAPI's `Depends()` system cleanly manages shared resources (DB pool, Kafka producer) across endpoints.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| Django REST Framework | Sync-first architecture. Async support is bolted on, not native. Heavier for a focused API service. |
| Flask | No native async support. Would require additional libraries (quart, gevent) for async operations. |
| Starlette (directly) | FastAPI adds validation, docs, and dependency injection on top of Starlette with minimal overhead. |

---

## 6. Frontend: React / Next.js Web Support Form

**Decision**: Standalone React component, buildable with Next.js for SSR if needed.

**Rationale**:
- **Required deliverable**: The spec and rubric explicitly require a React/Next.js web support form (10 points).
- **Component architecture**: The form is a self-contained component (SupportForm.jsx) that can be embedded in any React application.
- **Client-side validation**: React's state management makes real-time form validation straightforward.
- **Minimal scope**: Only one form component + status checker — not a full frontend application.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| Vue.js | Spec explicitly requires React/Next.js. |
| Svelte | Same — spec requirement. |
| Plain HTML/JS | Doesn't satisfy the React/Next.js requirement. |

---

## 7. Container Orchestration: Kubernetes (minikube)

**Decision**: Kubernetes manifests targeting minikube for local development and demonstration.

**Rationale**:
- **Required deliverable**: K8s deployment is worth 5 points directly and is essential for 24/7 readiness (10 points).
- **Auto-scaling**: HPA (Horizontal Pod Autoscaler) enables automatic scaling of API and worker pods based on CPU utilization.
- **Self-healing**: Liveness and readiness probes ensure unhealthy pods are restarted automatically. Kubernetes ensures desired replica count is maintained.
- **Secret management**: Kubernetes Secrets provide a standard way to inject credentials without hardcoding.
- **Service discovery**: K8s Services enable pods to find each other by DNS name (e.g., `postgres-svc:5432`).

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| Docker Compose only | No auto-scaling, no self-healing, no HPA. Insufficient for 24/7 readiness scoring. |
| AWS ECS | Cloud-provider specific. minikube allows local demonstration without cloud costs. |
| HashiCorp Nomad | Smaller ecosystem, fewer learning resources, less industry adoption than K8s. |

---

## 8. Testing Framework: pytest Ecosystem

**Decision**: pytest + pytest-asyncio + httpx + pytest-cov + unittest.mock

**Rationale**:
- **TDD mandate**: Constitution Principle III requires TDD with 80% coverage gate. pytest-cov enforces this.
- **Async testing**: pytest-asyncio enables `async def test_*` functions that work with asyncpg, aiokafka, and FastAPI's async endpoints.
- **HTTP testing**: httpx's `AsyncClient` integrates with FastAPI's `TestClient` for integration and contract tests without starting a real server.
- **Mocking**: unittest.mock patches external services (OpenAI API, Gmail API, Twilio API, Kafka) in unit tests. No real API calls during testing.
- **Fixtures**: pytest's fixture system enables shared test setup (DB connections, mock factories, test data).

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| unittest | More verbose, less flexible fixtures, no native async support. |
| nose2 | Smaller ecosystem, less community support than pytest. |
| Robot Framework | Designed for acceptance testing, overkill for unit/integration tests. |

---

## 9. Channel Architecture: Adapter Pattern

**Decision**: Abstract `ChannelHandler` base class with per-channel implementations.

**Rationale**:
- **Constitution Principle II**: Channel-agnostic core requires channel-specific behavior to be isolated in handler modules.
- **Pluggability**: Adding a new channel (e.g., Slack, SMS) means implementing one new handler class. No changes to the agent, database, or worker code.
- **Testability**: Each channel handler can be tested independently. Mock the handler interface for agent tests.
- **Responsibility separation**: Inbound parsing, response formatting, and delivery are channel concerns. The agent only deals with normalized messages and plain text responses.

**Design**:
```python
class ChannelHandler(ABC):
    @abstractmethod
    async def parse_inbound(self, raw_data: dict) -> InboundMessage: ...

    @abstractmethod
    async def format_response(self, response: str, metadata: dict) -> str: ...

    @abstractmethod
    async def deliver(self, formatted: str, destination: str, metadata: dict) -> bool: ...
```

---

## 10. Kafka Topic Design: Unified Incoming + Separate DLQ

**Decision**: Three topics — `fte.tickets.incoming`, `fte.tickets.outgoing`, `fte.tickets.dlq`

**Rationale**:
- **Simplicity**: All channels publish to one incoming topic with channel metadata. Workers don't need to subscribe to multiple topics.
- **DLQ for resilience**: Failed messages are published to a dead-letter queue rather than being lost. This satisfies Constitution Principle VI (Fail Gracefully).
- **Outgoing for async delivery**: Responses are published to an outgoing topic, enabling channel-specific delivery workers to handle email/WhatsApp API calls asynchronously.
- **Partition strategy**: Partition by customer_id to ensure messages from the same customer are processed in order by the same worker.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|-------------|
| Per-channel topics (fte.email.incoming, fte.whatsapp.incoming, etc.) | Unnecessary complexity. Channel metadata in the message payload is sufficient. |
| Single topic with no DLQ | Violates Principle VI — messages would be lost on processing failure. |
| Event sourcing with full replay | Overkill for a support system. Simple produce/consume is sufficient. |

---

## Summary of Resolved Decisions

| Area | Decision | Confidence |
|------|----------|------------|
| DB Driver | asyncpg (raw SQL) | High |
| Event Streaming | aiokafka | High |
| AI Agent | OpenAI Agents SDK (@function_tool) | High |
| Vector Search | pgvector in PostgreSQL | High |
| API Framework | FastAPI + uvicorn | High |
| Frontend | React/Next.js | High (required) |
| Orchestration | Kubernetes (minikube) | High (required) |
| Testing | pytest ecosystem | High |
| Channel Pattern | Adapter pattern (ABC) | High |
| Kafka Topics | 3 topics (incoming/outgoing/dlq) | High |

All NEEDS CLARIFICATION items have been resolved. No outstanding unknowns.
