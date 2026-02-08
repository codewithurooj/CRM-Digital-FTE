---
description: Execute full spec-driven workflow from specification to implementation with automatic skill/subagent routing
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Overview

This command orchestrates the **complete spec-driven development workflow**, automatically invoking the appropriate commands, skills, and subagents at each stage. It enforces TDD (Red-Green-Refactor) throughout implementation.

## Workflow Stages

```
+-------------+    +-------------+    +-------------+    +-------------+
| /sp.specify | -> |  /sp.plan   | -> |  /sp.tasks  | -> |/sp.auto-impl|
|             |    |             |    |             |    |             |
| Creates:    |    | Creates:    |    | Creates:    |    | Uses:       |
| - spec.md   |    | - plan.md   |    | - tasks.md  |    | - Skills    |
|             |    | - research.md|   |             |    | - Subagents |
|             |    | - contracts/|    |             |    | - TDD cycle |
+-------------+    +-------------+    +-------------+    +-------------+
       |                  |                  |                  |
       v                  v                  v                  v
   [CHECKPOINT]      [CHECKPOINT]      [CHECKPOINT]      [CHECKPOINT]
   User Review       User Review       User Review       Verify Tests
```

## Execution Modes

### Mode 1: Full Auto (Default)
```bash
/sp.workflow <feature-description>
```
Runs all stages automatically, pausing only for required user input.

### Mode 2: Step-by-Step
```bash
/sp.workflow <feature-description> --step
```
Pauses after each stage for user approval before continuing.

### Mode 3: Resume from Stage
```bash
/sp.workflow --resume plan
```
Resumes from a specific stage (spec, plan, tasks, implement).

---

## Outline

### Stage 0: Initialize Feature

1. Parse user input for feature description
2. Create feature directory structure:
   ```
   specs/<feature-name>/
   ├── spec.md          # Created in Stage 1
   ├── plan.md          # Created in Stage 2
   ├── tasks.md         # Created in Stage 3
   ├── research.md      # Created in Stage 2
   ├── data-model.md    # Created in Stage 2
   ├── contracts/       # Created in Stage 2
   └── checklists/      # Optional
   ```
3. Report: "Feature directory initialized at specs/<feature-name>/"

### Stage 1: Specification (`/sp.specify`)

**Invoke:** `/sp.specify <feature-description>`

**Expected Output:**
- `spec.md` with functional requirements, user stories, acceptance criteria

**Checkpoint:**
- Display spec.md summary
- Ask: "Proceed to planning? (yes/no/edit)"
- If "edit" -> Allow user to provide feedback, re-run specify

**ADR Check:**
- If significant architectural decisions detected -> Suggest `/sp.adr`

### Stage 2: Planning (`/sp.plan`)

**Invoke:** `/sp.plan`

**Expected Output:**
- `plan.md` - Technical architecture
- `research.md` - Technology decisions
- `data-model.md` - Entity definitions (CRM schema: customers, conversations, messages, tickets, knowledge_base)
- `contracts/` - API specifications (webhook endpoints, support form API, metrics)

**Skill/Subagent Triggers:**
- API design detected -> Load `stateless-api-designer` agent
- Database schema needed -> Load `db-migrator` agent context
- AI agent architecture -> Load `agent-orchestrator` agent context

**Checkpoint:**
- Display plan summary (tech stack, architecture)
- Ask: "Proceed to task generation? (yes/no/edit)"

**ADR Check:**
- Multiple architectural decisions -> Suggest `/sp.adr` for each

### Stage 3: Task Generation (`/sp.tasks`)

**Invoke:** `/sp.tasks`

**Expected Output:**
- `tasks.md` with phased, dependency-ordered tasks

**Skill Detection:**
For each generated task, annotate with detected skill:
```markdown
- [ ] T-001: Create PostgreSQL CRM schema [AGENT: db-migrator]
- [ ] T-002: Build Customer Success AI agent [AGENT: agent-orchestrator]
- [ ] T-003: Create Web Support Form [SKILL: nextjs-betterauth]
- [ ] T-004: Build Gmail webhook handler [SKILL: fastapi-sqlmodel]
- [ ] T-005: Set up Kafka message processor [AGENT: microservice-scaffolder]
- [ ] T-006: Build WhatsApp handler [SKILL: fastapi-sqlmodel]
- [ ] T-007: Create Docker containers [SKILL: dockerfile-generator]
- [ ] T-008: Deploy to Kubernetes [SKILL: helm-chart-builder]
```

**Checkpoint:**
- Display task summary (count by phase, skill distribution)
- Ask: "Proceed to implementation? (yes/no/edit)"

### Stage 4: Implementation (`/sp.auto-implement`)

**Invoke:** `/sp.auto-implement`

**Execution:**
1. Load skill registry from `.claude/skill-registry.md`
2. Load constitution for TDD enforcement
3. For each task:
   - Detect skill from annotation or pattern matching
   - Load skill instructions
   - Execute TDD cycle: RED (failing test) -> GREEN (pass) -> REFACTOR
   - Run `pytest --cov --cov-fail-under=80` after each task
   - Mark task complete in tasks.md
4. Report progress after each phase

**Skill Loading Order:**
1. Check task annotation: `[SKILL: name]` or `[AGENT: name]`
2. If no annotation, pattern match against skill registry
3. If no match, use default implementation approach

**Progress Reporting:**
```
Phase 1: Setup ============ 100%
  T-001: Project initialization
  T-002: Dependencies installed

Phase 2: Database ========== 100%
  T-003: PostgreSQL CRM schema [db-migrator]
  T-004: Database queries layer [db-migrator]

Phase 3: Agent ========.... 80%
  T-005: AI Agent core [agent-orchestrator]
  T-006: Agent tools (5 tools) [mcp-builder]
  .. T-007: Agent testing [nl-test-generator]
```

### Stage 5: Verification

After implementation:

1. **Run Tests (TDD Gate):**
   ```bash
   pytest production/tests/ -v --cov=production --cov-fail-under=80
   ```

2. **Analyze Artifacts:**
   - Invoke `/sp.analyze` to check consistency

3. **Final Report:**
   ```markdown
   ## Workflow Complete

   ### Feature: <feature-name>

   | Stage | Status | Artifacts |
   |-------|--------|-----------|
   | Specify | Done | spec.md |
   | Plan | Done | plan.md, research.md, contracts/ |
   | Tasks | Done | tasks.md (N tasks) |
   | Implement | Done | N files generated |
   | Verify | Done | All tests passing, coverage >= 80% |

   ### Skills Used
   - db-migrator: N tasks
   - agent-orchestrator: N tasks
   - fastapi-sqlmodel: N tasks
   - nextjs-betterauth: N tasks
   - microservice-scaffolder: N tasks

   ### CRM Build Order Compliance
   - Context files: Done
   - PostgreSQL schema: Done
   - AI Agent + Tools: Done
   - Web Support Form: Done
   - Kafka Pipeline: Done
   - Gmail Channel: Done
   - WhatsApp Channel: Done
   - K8s Deployment: Done

   ### Next Steps
   - Deploy: Build Docker images and deploy to K8s
   - 24-hour test: Run Locust load tests
   - Documentation: Update discovery log
   ```

---

## Error Handling

### Stage Failure
If any stage fails:
1. Stop workflow
2. Report error with context
3. Suggest fix or manual intervention
4. Provide resume command: `/sp.workflow --resume <stage>`

### Skill Not Found
If skill file missing:
1. Warn: "Skill <name> not found"
2. Fallback to default implementation
3. Continue workflow

### TDD Gate Failure
If coverage drops below 80%:
1. Stop implementation
2. Report uncovered code
3. Require test additions before proceeding

### User Abort
If user says "no" at checkpoint:
1. Stop workflow
2. Save progress
3. Provide resume command

---

## Command Chaining

This workflow internally chains these commands:

```
/sp.specify -> /sp.plan -> /sp.tasks -> /sp.auto-implement -> /sp.analyze
     |             |           |              |                |
     |             |           |              |                +-- Verify
     |             |           |              +-- Uses skill registry + TDD
     |             |           +-- Annotates tasks with skills
     |             +-- Triggers api-designer, db-migrator, agent-orchestrator
     +-- Creates spec.md
```

---

## Examples

### Example 1: Full CRM Feature
```bash
User: /sp.workflow Build Gmail channel integration with webhook handler and AI processing

Claude:
Stage 0: Initializing feature directory...
Created: specs/gmail-channel/

Stage 1: Running /sp.specify...
Created: spec.md
Summary: 5 user stories, 12 acceptance criteria

Proceed to planning? (yes/no/edit)
> yes

Stage 2: Running /sp.plan...
Created: plan.md, research.md, data-model.md, contracts/
Tech Stack: FastAPI, asyncpg, aiokafka, OpenAI Agents SDK
ADR suggestion: "Gmail Pub/Sub vs Polling" - Document? Run /sp.adr

Proceed to tasks? (yes/no/edit)
> yes

Stage 3: Running /sp.tasks...
Created: tasks.md
Tasks: 10 total
  - Backend API (fastapi-sqlmodel): 3
  - Database (db-migrator): 2
  - Microservice (microservice-scaffolder): 2
  - Agent (agent-orchestrator): 1
  - Testing (nl-test-generator): 2

Proceed to implementation? (yes/no/edit)
> yes

Stage 4: Running /sp.auto-implement with TDD...
[RED -> GREEN -> REFACTOR for each task]

Stage 5: Verification...
All tests passing
Coverage: 85% (gate: 80%) PASS

## Workflow Complete!
```

### Example 2: Resume from Plan
```bash
User: /sp.workflow --resume plan

Claude:
Resuming workflow from Stage 2 (Plan)...
Found existing spec.md
Running /sp.plan...
[Continues from plan stage]
```

---

## PHR Creation

As each stage completes, create a PHR:

- Stage 1 (Specify): Stage = `spec`
- Stage 2 (Plan): Stage = `plan`
- Stage 3 (Tasks): Stage = `tasks`
- Stage 4 (Implement): Stage = `green`

Final PHR summarizes entire workflow.
