---
id: 002
title: Add Skill Registry Auto-Trigger Setup
stage: general
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: none
branch: 001-project-setup
user: pc1
command: /sp.constitution
labels: ["skill-registry", "auto-implement", "workflow", "agents", "skills"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skill-registry.md
  - .claude/commands/sp.auto-implement.md
  - .claude/commands/sp.workflow.md
  - .claude/agents/ (12 agent definitions)
  - .claude/skills/ (12 skill definitions)
tests:
  - N/A
---

## Prompt

i want that agents or skills should auto trigger without myself telling in my another project at this project i used skills registry file can i use that file for this project also C:\Users\pc1\Desktop\reusable-intelligence\.claude

## Response snapshot

Created a CRM-specific skill registry and two workflow commands adapted from the reusable-intelligence project:

1. `.claude/skill-registry.md` — Maps 10 skills and 10 subagents to CRM components with trigger keywords for auto-detection. Includes Quick Reference lookup table, CRM Digital FTE Project Mapping (16 components to primary/secondary skills), and pattern matching pseudo-code.

2. `/sp.auto-implement` command — Extends `/sp.implement` with automatic task-type detection. Matches task descriptions against skill registry patterns, loads corresponding skill instructions, and executes with TDD enforcement (RED-GREEN-REFACTOR). Supports manual overrides via `[SKILL: name]` or `[AGENT: name]` annotations.

3. `/sp.workflow` command — Full pipeline orchestrator: /sp.specify -> /sp.plan -> /sp.tasks -> /sp.auto-implement -> /sp.analyze. Three modes: Full Auto, Step-by-Step (checkpoints), Resume. Enforces 80% coverage gate and CRM build order compliance.

Also committed all 12 agent definitions and 12 skill definitions (82 files total).

## Outcome

- Impact: Auto-triggering infrastructure complete — skills/agents will be detected and invoked automatically during `/sp.auto-implement` and `/sp.workflow`
- Tests: N/A (infrastructure/configuration artifact)
- Files: .claude/skill-registry.md, .claude/commands/sp.auto-implement.md, .claude/commands/sp.workflow.md, 12 agents, 12 skills (82 files)
- Next prompts: Begin Step 1 of build order — create context files (company-profile.md, product-docs.md, sample-tickets.json)
- Reflection: Adapted from reusable-intelligence project; CRM-specific patterns (channel handlers, agent tools, webhook endpoints) now mapped to correct skills

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
