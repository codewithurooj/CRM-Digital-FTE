# Skill & Subagent Registry — CRM Digital FTE

This registry maps task patterns to the appropriate skills and subagents for automatic invocation.

## Quick Reference

```
Task mentions "FastAPI", "backend", "routes"     → Use fastapi-sqlmodel skill
Task mentions "database", "migration", "schema"  → Use db-migrator agent
Task mentions "AI agent", "OpenAI SDK", "tools"  → Use agent-orchestrator agent
Task mentions "Kafka", "consumer", "event"        → Use microservice-scaffolder agent
Task mentions "Next.js", "React", "form"          → Use nextjs-betterauth skill
Task mentions "Dockerfile", "container"           → Use dockerfile-generator skill
Task mentions "Helm", "K8s", "Kubernetes"         → Use helm-chart-builder skill
Task mentions "API design", "contract"            → Use stateless-api-designer agent
Task mentions "test", "E2E", "pytest"             → Use nl-test-generator agent
Task mentions "conversation", "chat history"      → Use conversation-manager skill
Task mentions "MCP", "tool server"                → Use mcp-server-creator skill
Task mentions "kubectl", "cluster"                → Use kubectl-ai skill
```

---

## Skills (`.claude/skills/`)

### 1. fastapi-sqlmodel
**Path:** `.claude/skills/fastapi-sqlmodel.md`
**Triggers:** `FastAPI`, `backend`, `routes`, `endpoints`, `API`, `SQLModel`, `CRUD`
**CRM Usage:** Build API endpoints — `/support/submit`, `/webhooks/gmail`, `/webhooks/whatsapp`, `/health`, `/metrics/channels`
**Generates:**
- `production/api/main.py`
- `production/database/queries.py`
- `production/channels/web_form_handler.py`
- `production/tests/`

### 2. conversation-manager
**Path:** `.claude/skills/conversation-manager.md`
**Triggers:** `conversation`, `chat history`, `message storage`, `session`, `context`
**CRM Usage:** Manage customer conversations across channels — store messages, retrieve history, track sentiment, handle cross-channel continuity
**Generates:**
- Conversation lifecycle management
- Message storage and retrieval
- Cross-channel history merging

### 3. dockerfile-generator
**Path:** `.claude/skills/dockerfile-generator.md`
**Triggers:** `Dockerfile`, `container`, `image`, `Docker`, `containerize`
**CRM Usage:** Containerize the FastAPI app and Kafka worker
**Generates:**
- `production/Dockerfile`
- `production/.dockerignore`

### 4. helm-chart-builder
**Path:** `.claude/skills/helm-chart-builder.md`
**Triggers:** `Helm`, `chart`, `Kubernetes`, `K8s`, `deployment`, `values.yaml`
**CRM Usage:** Deploy API pods, worker pods, PostgreSQL, Kafka to Kubernetes
**Generates:**
- `production/k8s/` manifests
- HPA, services, ingress configs

### 5. jwt-validator
**Path:** `.claude/skills/jwt-validator.md`
**Triggers:** `JWT`, `auth`, `token`, `authentication`, `authorization`
**CRM Usage:** Secure API endpoints (webhook validation, API auth)

### 6. kubectl-ai
**Path:** `.claude/skills/kubectl-ai.md`
**Triggers:** `kubectl`, `cluster`, `pod`, `scale`, `deploy`, `k8s ops`
**CRM Usage:** Manage K8s cluster during deployment and 24-hour test

### 7. kagent
**Path:** `.claude/skills/kagent.md`
**Triggers:** `cluster health`, `k8s monitoring`, `resource audit`, `security audit`
**CRM Usage:** Monitor cluster health during 24-hour continuous operation test

### 8. mcp-server-creator
**Path:** `.claude/skills/mcp-server-creator/SKILL.md`
**Triggers:** `MCP`, `Model Context Protocol`, `tool server`
**CRM Usage:** Build the MCP server prototype during incubation phase (5 tools)

### 9. nextjs-betterauth
**Path:** `.claude/skills/nextjs-betterauth.md`
**Triggers:** `Next.js`, `frontend`, `React`, `components`, `form`, `UI`
**CRM Usage:** Build the Web Support Form (React/Next.js component — REQUIRED, 10 points)

### 10. spec-writer
**Path:** `.claude/skills/spec-writer.md`
**Triggers:** `specification`, `feature spec`, `requirements doc`
**CRM Usage:** Generate `specs/customer-success-fte-spec.md`

---

## Subagents (`.claude/agents/`)

### 1. agent-orchestrator
**Path:** `.claude/agents/agent-orchestrator/agent.md`
**Triggers:** `AI agent`, `orchestrator`, `OpenAI SDK`, `tool calling`, `agent workflow`
**CRM Usage:** Design the Customer Success agent — tool execution order, escalation logic, channel-aware prompts, conversation flow
**Output:** Agent architecture, tool definitions, system prompt

### 2. db-migrator
**Path:** `.claude/agents/db-migrator/agent.md`
**Triggers:** `database`, `migration`, `schema`, `ALTER TABLE`, `PostgreSQL`
**CRM Usage:** Build and migrate the CRM schema — customers, conversations, messages, tickets, knowledge_base, customer_identifiers
**Output:** Migration scripts, rollback scripts, queries.py

### 3. microservice-scaffolder
**Path:** `.claude/agents/microservice-scaffolder/agent.md`
**Triggers:** `Kafka consumer`, `microservice`, `event-driven`, `pub/sub`, `worker`
**CRM Usage:** Scaffold the unified message processor (Kafka consumer that runs the AI agent)
**Output:** `production/workers/message_processor.py` with Dockerfile, tests

### 4. stateless-api-designer
**Path:** `.claude/agents/stateless-api-designer/agent.md`
**Triggers:** `API design`, `REST contract`, `OpenAPI`, `API specification`
**CRM Usage:** Design FastAPI endpoint contracts — webhook handlers, support form API, metrics API
**Output:** OpenAPI specs, endpoint documentation

### 5. nl-test-generator
**Path:** `.claude/agents/nl-test-generator/agent.md`
**Triggers:** `Given-When-Then`, `BDD`, `test scenarios`, `acceptance criteria`, `TDD`
**CRM Usage:** Generate TDD test cases from requirements — agent behavior tests, channel handler tests, E2E tests
**Output:** Test specs in Given-When-Then format, pytest test files

### 6. testing-agent
**Path:** `.claude/agents/testing-agent/README.md`
**Triggers:** `E2E test`, `integration test`, `test suite`, `automated testing`
**CRM Usage:** Execute comprehensive E2E tests across all channels
**Output:** Test results, diagnostic reports

### 7. mcp-builder
**Path:** `.claude/agents/mcp-builder/agent.md`
**Triggers:** `MCP tool`, `tool interface`, `context protocol design`
**CRM Usage:** Design the 5 MCP tools (search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, send_response)
**Output:** Tool specifications, parameter schemas

### 8. helm-updater
**Path:** `.claude/agents/helm-updater/agent.md`
**Triggers:** `helm upgrade`, `add env var`, `update values`, `chart update`
**CRM Usage:** Update K8s deployment configs as features are added
**Output:** Updated values.yaml, deployment changes

### 9. dapr-generator
**Path:** `.claude/agents/dapr-generator/agent.md`
**Triggers:** `Dapr`, `state store`, `pubsub component`
**CRM Usage:** Optional — only if adopting Dapr for service communication

### 10. ui-ux-agent
**Path:** `.claude/agents/ui-ux-agent.md`
**Triggers:** `UI design`, `UX`, `styling`, `component design`
**CRM Usage:** Polish the Web Support Form UI

---

## CRM Digital FTE Project Mapping

| CRM Component | Primary Skill/Agent | Secondary |
|---------------|---------------------|-----------|
| PostgreSQL CRM Schema | db-migrator | fastapi-sqlmodel |
| AI Agent (OpenAI SDK) | agent-orchestrator | mcp-builder |
| Agent Tools (5 tools) | mcp-builder | agent-orchestrator |
| FastAPI Endpoints | fastapi-sqlmodel | stateless-api-designer |
| Web Support Form (REQUIRED) | nextjs-betterauth | ui-ux-agent |
| Gmail Handler | fastapi-sqlmodel | stateless-api-designer |
| WhatsApp Handler | fastapi-sqlmodel | stateless-api-designer |
| Kafka Streaming | microservice-scaffolder | - |
| Message Processor Worker | microservice-scaffolder | conversation-manager |
| Conversation History | conversation-manager | db-migrator |
| Docker Containerization | dockerfile-generator | - |
| Kubernetes Deployment | helm-chart-builder | helm-updater |
| K8s Operations | kubectl-ai | kagent |
| TDD Test Suite | nl-test-generator | testing-agent |
| E2E Channel Tests | testing-agent | nl-test-generator |
| API Contracts | stateless-api-designer | spec-writer |

---

## Usage in Commands

### In `/sp.auto-implement`:
```python
# Skill detection for CRM Digital FTE tasks
def detect_skill(task_description):
    patterns = {
        'fastapi-sqlmodel': ['FastAPI', 'backend', 'routes', 'API', 'endpoint'],
        'conversation-manager': ['conversation', 'chat history', 'message storage'],
        'dockerfile-generator': ['Dockerfile', 'container', 'Docker'],
        'helm-chart-builder': ['Helm', 'chart', 'K8s', 'Kubernetes', 'deployment'],
        'nextjs-betterauth': ['Next.js', 'frontend', 'React', 'form', 'component'],
        'kubectl-ai': ['kubectl', 'cluster', 'pod', 'scale'],
        'mcp-server-creator': ['MCP', 'tool server'],
        'db-migrator': ['migration', 'schema', 'database', 'PostgreSQL', 'table'],
        'agent-orchestrator': ['AI agent', 'orchestrator', 'OpenAI SDK', 'tool calling'],
        'microservice-scaffolder': ['Kafka', 'consumer', 'microservice', 'worker'],
        'nl-test-generator': ['test', 'TDD', 'Given-When-Then', 'pytest'],
        'stateless-api-designer': ['API design', 'contract', 'OpenAPI'],
        'testing-agent': ['E2E test', 'integration test', 'test suite'],
    }

    for skill, keywords in patterns.items():
        if any(kw.lower() in task_description.lower() for kw in keywords):
            return skill
    return 'default'
```

### Manual Override in tasks.md:
```markdown
- [ ] T-005: Build Kafka message processor [AGENT: microservice-scaffolder]
- [ ] T-006: Design Customer Success agent [AGENT: agent-orchestrator]
```

---

## Adding New Skills/Agents

1. Create skill file in `.claude/skills/{name}.md` or agent in `.claude/agents/{name}/`
2. Add entry to this registry with triggers and CRM usage
3. Update pattern matching in `/sp.auto-implement`
