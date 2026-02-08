---
description: Automatically implement tasks using the appropriate skills and subagents based on task type detection
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Overview

This command extends `/sp.implement` by **automatically detecting task types** and invoking the appropriate skills/subagents for each task. It uses the skill registry at `.claude/skill-registry.md` for pattern matching.

## Skill & Subagent Router

### Detection Rules

When processing each task from `tasks.md`, detect the task type and invoke the corresponding skill/subagent:

| Task Pattern | Detected Type | Skill/Subagent to Use |
|--------------|---------------|----------------------|
| "FastAPI", "backend", "routes", "endpoints", "API", "CRUD" | Backend API | `.claude/skills/fastapi-sqlmodel.md` |
| "Next.js", "frontend", "React", "form", "UI", "component" | Frontend | `.claude/skills/nextjs-betterauth.md` |
| "Helm", "chart", "Kubernetes", "K8s", "deployment" | K8s Deployment | `.claude/skills/helm-chart-builder.md` |
| "database", "migration", "schema", "PostgreSQL", "table" | Database | `.claude/agents/db-migrator/agent.md` |
| "Kafka", "consumer", "event", "pub/sub", "microservice", "worker" | Microservice | `.claude/agents/microservice-scaffolder/agent.md` |
| "AI agent", "orchestrator", "OpenAI SDK", "tool calling", "agent workflow" | AI Agent | `.claude/agents/agent-orchestrator/agent.md` |
| "MCP", "tool server", "Model Context Protocol" | MCP Server | `.claude/skills/mcp-server-creator/SKILL.md` |
| "test", "E2E", "integration test", "pytest", "TDD" | Testing | `.claude/agents/nl-test-generator/agent.md` |
| "API design", "contract", "OpenAPI" | API Design | `.claude/agents/stateless-api-designer/agent.md` |
| "Dockerfile", "container", "image", "Docker" | Containerization | `.claude/skills/dockerfile-generator.md` |
| "values.yaml", "helm upgrade", "annotations" | Helm Update | `.claude/agents/helm-updater/agent.md` |
| "conversation", "chat history", "message storage", "session" | Conversation | `.claude/skills/conversation-manager.md` |
| "JWT", "auth", "token", "authentication" | Auth | `.claude/skills/jwt-validator.md` |
| "kubectl", "cluster", "pod", "scale" | K8s Ops | `.claude/skills/kubectl-ai.md` |

### Execution Flow

```
1. Parse tasks.md -> Extract all tasks with [PENDING] / [ ] status
2. For each task:
   a. Check for manual override: [SKILL: name] or [AGENT: name]
   b. If no override, detect task type using pattern matching
   c. Load corresponding skill/subagent instructions
   d. Execute task following skill guidelines
   e. Run tests (TDD: ensure tests pass before marking done)
   f. Mark task as [X] in tasks.md
   g. Create PHR for the task
3. If task type is unknown -> use default implementation approach
4. Report progress after each phase
```

## Outline

### Step 1: Load Context

1. Load the skill registry: `.claude/skill-registry.md`
2. Load feature context:
   - `tasks.md` - Task list
   - `plan.md` - Architecture and tech stack
   - `spec.md` - Requirements
3. Load constitution: `.specify/memory/constitution.md` (for TDD rules)

### Step 2: Analyze Tasks

For each task in tasks.md:

```markdown
## Task Analysis

| Task ID | Description | Detected Type | Skill/Subagent |
|---------|-------------|---------------|----------------|
| T-001   | Create PostgreSQL CRM schema | Database | db-migrator |
| T-002   | Build AI Agent with OpenAI SDK | AI Agent | agent-orchestrator |
| T-003   | Create Web Support Form | Frontend | nextjs-betterauth |
| T-004   | Build Gmail webhook handler | Backend API | fastapi-sqlmodel |
| T-005   | Set up Kafka message processor | Microservice | microservice-scaffolder |
```

### Step 3: Execute with Skills (TDD Enforced)

For each task, follow this pattern:

```markdown
### Executing Task: {task_id}

**Type Detected:** {type}
**Skill Loaded:** {skill_path}
**TDD Phase:** RED -> GREEN -> REFACTOR

**Step 1 - RED:** Write failing test
{Generate test based on task requirements}

**Step 2 - GREEN:** Implement minimum code
{Read and follow skill guidelines, implement just enough to pass}

**Step 3 - REFACTOR:** Clean up
{Refactor while tests stay green}

**Verification:**
{Run pytest, confirm tests pass, check coverage}

**Status:** Done
```

### Step 4: Skill Invocation Examples (CRM-Specific)

#### Database Task (db-migrator)
```
1. Read `.claude/agents/db-migrator/agent.md`
2. Extract schema from task (e.g., customers, conversations, messages)
3. Generate:
   - production/database/migrations/
   - production/database/queries.py
   - production/tests/unit/test_queries.py
4. Follow PostgreSQL + asyncpg patterns
```

#### AI Agent Task (agent-orchestrator)
```
1. Read `.claude/agents/agent-orchestrator/agent.md`
2. Extract agent requirements (tools, escalation, channel-awareness)
3. Generate:
   - production/agent/agent.py
   - production/agent/tools.py
   - production/agent/prompts.py
   - production/tests/unit/test_agent.py
4. Follow OpenAI Agents SDK @function_tool pattern
```

#### Backend API Task (fastapi-sqlmodel)
```
1. Read `.claude/skills/fastapi-sqlmodel.md`
2. Extract resource from task (e.g., webhook handler, support form API)
3. Generate:
   - production/api/main.py
   - production/channels/{channel}_handler.py
   - production/tests/integration/test_{endpoint}.py
4. Follow async FastAPI + asyncpg patterns
```

#### Frontend Task (nextjs-betterauth)
```
1. Read `.claude/skills/nextjs-betterauth.md`
2. Extract component from task (Web Support Form)
3. Generate:
   - frontend/app/support/page.tsx
   - frontend/components/SupportForm.tsx
   - frontend/lib/api/support.ts
4. Include form validation, channel-appropriate formatting
```

#### Kafka Task (microservice-scaffolder)
```
1. Read `.claude/agents/microservice-scaffolder/agent.md`
2. Extract worker purpose (unified message processor)
3. Generate:
   - production/workers/message_processor.py
   - production/workers/Dockerfile
   - production/tests/integration/test_processor.py
4. Follow aiokafka consumer pattern
```

### Step 5: Progress Tracking

After each task completion:

1. Update tasks.md: Change `[ ]` to `[X]`
2. Log to console:
   ```
   T-001: Create PostgreSQL CRM schema
      Skill: db-migrator
      Files: production/database/queries.py, production/database/migrations/
      Tests: 5 passed, coverage 87%
   ```
3. If task fails or tests fail, stop and report error
4. Never mark a task done if tests are failing (TDD mandate)

### Step 6: Completion Report

```markdown
## Implementation Complete

### Summary
- Total Tasks: {count}
- Completed: {count}
- Failed: 0

### Skills Used
| Skill | Tasks | Files Generated |
|-------|-------|-----------------|
| db-migrator | 2 | 6 files |
| agent-orchestrator | 2 | 8 files |
| fastapi-sqlmodel | 4 | 12 files |
| nextjs-betterauth | 1 | 4 files |
| microservice-scaffolder | 2 | 6 files |

### Test Results
- Total Tests: {count}
- Passed: {count}
- Coverage: {percentage}%
- Coverage Gate (80%): PASS/FAIL

### Next Steps
- Run `/sp.analyze` to verify consistency
- Run full test suite: `pytest production/tests/ --cov --cov-fail-under=80`
- Deploy: Build Docker images and deploy to K8s
```

## Error Handling

If skill file not found:
```
Warning: Skill not found: {skill_path}
Falling back to default implementation approach.
```

If task type cannot be detected:
```
Warning: Unknown task type for: {task_description}
Using general implementation approach.
Please specify skill manually if needed.
```

If tests fail (TDD violation):
```
ERROR: Tests failing for task {task_id}
TDD mandate: Cannot mark task complete with failing tests.
Fix implementation and re-run.
```

## Manual Skill Override

User can specify skill in task description:

```markdown
- [ ] T-005: Create message processor [SKILL: microservice-scaffolder]
- [ ] T-006: Design agent workflow [AGENT: agent-orchestrator]
```

This overrides auto-detection.

---

## PHR Creation

As the main request completes, you MUST create and complete a PHR (Prompt History Record).

1) Stage: `green` (implementation)
2) Title: Generate 3-7 word title
3) Route: `history/prompts/<feature-name>/`
4) Create PHR with full PROMPT_TEXT and RESPONSE_TEXT
