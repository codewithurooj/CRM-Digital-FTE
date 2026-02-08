---
id: PHR-004
title: dependency-ordered-task-generation
stage: tasks
date: 2026-02-08
surface: cli
model: claude-opus-4-6
feature: 002-customer-success-agent
branch: 002-customer-success-agent
user: architect
command: /sp.tasks
labels: [tasks, dependency-chain, tdd, skill-registry, scoring-rubric]
links:
  spec: specs/002-customer-success-agent/spec.md
  ticket: n/a
  adr: n/a
  pr: n/a
files:
  - specs/002-customer-success-agent/tasks.md (created)
tests:
  - n/a (task generation, no code written)
---

## Prompt

Generate dependency-ordered tasks for CRM Digital FTE. Read the plan at specs/crm-digital-fte/plan.md and spec at specs/crm-digital-fte/spec.md. Annotate each task with the appropriate [SKILL: name] or [AGENT: name] from .claude/skill-registry.md. Follow the build order from constitution: Context → DB → Agent → Web Form → Kafka → Gmail → WhatsApp → K8s. Group into phases. Every task must have a clear TDD target (what test to write first). Include all 10 scoring categories — miss nothing.

## Response snapshot

Generated `specs/002-customer-success-agent/tasks.md` with 118 dependency-ordered tasks across 15 phases. Tasks organized by user story (US1-US12) following the constitution build order. Every task annotated with [SKILL: x] or [AGENT: x] from skill-registry.md. All 12 scoring categories mapped to specific task ranges. TDD targets specified for each implementation task. Parallel opportunities identified (30+ [P] tasks). MVP scope defined as Phases 1-4 (52 tasks covering Web Form + Agent Core = 30+ points).

## Outcome

- ✅ Impact: Complete task breakdown for full CRM Digital FTE implementation, executable by LLM agents
- 🧪 Tests: TDD targets specified for every implementation task (test file paths included)
- 📁 Files: 1 file created — specs/002-customer-success-agent/tasks.md
- 🔁 Next prompts: `/sp.implement` to begin Phase 1, or `/sp.auto-implement` for automated execution
- 🧠 Reflection: Plan and spec paths were at specs/002-customer-success-agent/ not specs/crm-digital-fte/ — the prerequisite check correctly resolved this. All 12 scoring categories covered with explicit task-to-category mapping.

## Evaluation notes (flywheel)

- Failure modes observed: Path mismatch in user prompt vs actual feature dir (handled by check-prerequisites script)
- Graders run and results (PASS/FAIL): Format validation PASS — all 118 tasks have checkbox, ID, description with file path
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Consider adding time estimates per phase for hackathon planning
