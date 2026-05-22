# Transition Checklist: General Agent → Custom Agent

> **Project**: CRM Digital FTE  
> **Transition Date**: 2026-02-08  
> **From**: Claude Code (General Agent / Incubation Phase)  
> **To**: OpenAI Agents SDK (Custom Agent / Specialization Phase)

---

## 1. Discovered Requirements

All requirements discovered during incubation via `specs/discovery-log.md`:

- [x] Channel determines *tone*, not *content* — same issues arrive via all 3 channels
- [x] 60% of tickets are answerable directly from the knowledge base
- [x] WhatsApp messages are short and casual; email is formal and detailed
- [x] Pricing questions must NEVER be answered — hard escalation required
- [x] Sentiment scoring needed on every message (score < 0.3 = escalate)
- [x] Customer identity must be unified across email/phone/WhatsApp
- [x] Cross-channel conversation history is critical for repeat customers
- [x] Ticket must be created BEFORE any response (audit trail requirement)
- [x] Agent needs fallback response when KB has no match (escalate after 2 attempts)
- [x] WhatsApp "human" / "agent" keywords must trigger live agent handoff

---

## 2. Working Prompts

### System Prompt (production)

See `production/agent/prompts.py:SYSTEM_PROMPT` — extracted from incubation and formalized with:
- Explicit tool call order (create_ticket → get_history → search_kb → send_response)
- Hard constraints block (pricing, refunds, legal)
- Channel-aware formatting instructions
- Escalation trigger list

### Tool Descriptions That Worked

Key docstring pattern from incubation:
- Lead with *when to use* (helps LLM decide)
- Then *Args* block with exact value sets
- Never omit the `ALWAYS` / `NEVER` constraints in the docstring

---

## 3. Edge Cases Found

| Edge Case | How Handled | Test |
|-----------|-------------|------|
| Empty message | Agent returns clarification prompt | `test_unit/test_agent_tools.py` |
| Pricing question | Hard guardrail fires before agent runs | `test_unit/test_guardrails.py` |
| Angry customer (profanity) | Guardrail triggers `abusive_language` escalation | `test_unit/test_guardrails.py` |
| WhatsApp "human" keyword | Guardrail → `human_request` escalation | `test_unit/test_guardrails.py` |
| Legal threat ("sue", "lawyer") | Guardrail → `legal_threat` escalation | `test_unit/test_guardrails.py` |
| KB returns no results | After 2 attempts, agent escalates with `no_kb_match` | `test_unit/test_agent_tools.py` |
| Response too long for WhatsApp | `format_response` truncates at 1,600 chars | `test_unit/test_formatters.py` |
| Same customer across channels | `resolve_customer` links via `customer_identifiers` | `test_integration/test_cross_channel_identity.py` |
| Agent processing error | Fallback response sent; message pushed to DLQ | `test_unit/test_message_processor.py` |
| Duplicate Pub/Sub notification | Idempotent ticket creation (unique channel_message_id) | `test_contract/test_gmail_webhook_contract.py` |

---

## 4. Response Patterns

| Channel | Pattern | Example |
|---------|---------|---------|
| **Email** | Formal greeting + detailed body + ticket ref + signature | `Hi Alice,\n\n[answer]\n\nTicket: TK-001\n\nBest regards, TechCorp Support` |
| **WhatsApp** | Direct answer + ticket ref (no greeting/signature) | `[answer]\n\nTicket: TK-001` |
| **Web Form** | Semi-formal greeting + body + ticket ref | `Hi Alice,\n\n[answer]\n\nTicket: TK-001` |

---

## 5. Escalation Rules (Finalized)

| Trigger | Reason Code | Notes |
|---------|-------------|-------|
| Keywords: pricing, cost, how much, plan price | `pricing_inquiry` | Hard constraint — fires in guardrail before agent |
| Keywords: refund, money back, charge | `refund_request` | Hard constraint |
| Keywords: lawyer, legal, sue, attorney | `legal_threat` | Hard constraint |
| Keywords: cancel, cancellation | `pricing_inquiry` | Routed to billing team |
| Sentiment score < 0.3 | `negative_sentiment` | Soft trigger — measured per message |
| WhatsApp body = "human", "agent", "representative" | `human_request` | Exact match |
| Email body contains "human support" | `human_request` | Substring match |
| KB returns empty after 2 searches | `no_kb_match` | Agent decides |
| Profanity detected | `abusive_language` | Hard constraint |
| Data security keywords | `data_security` | Hard constraint |

---

## 6. Performance Baseline

Measured during incubation prototype testing:

| Metric | Baseline | Target |
|--------|----------|--------|
| Agent response time (in-process) | ~1.5–2.5 s | < 3 s |
| End-to-end delivery (web form) | ~3–5 s | < 30 s |
| KB accuracy on test set (20 tickets) | ~85% | > 85% |
| Escalation rate on test set | ~18% | < 20% |
| Cross-channel match accuracy | 100% (email-to-email) | > 95% |

---

## Transition Steps Completed

### From Incubation
- [x] Working prototype that handles basic queries
- [x] Documented edge cases (10 found, listed above)
- [x] Working system prompt (formalized in `prompts.py`)
- [x] MCP tools defined and tested (`mcp_server.py`)
- [x] Channel-specific response patterns identified
- [x] Escalation rules finalized
- [x] Performance baseline measured

### Transition Steps
- [x] Production folder structure created
- [x] Prompts extracted to `agent/prompts.py`
- [x] MCP tools converted to `@function_tool` in `agent/tools.py`
- [x] Error handling added to all tools (try/except with fallbacks)
- [x] Pydantic validation on all API inputs (FastAPI schemas)
- [x] Transition test suite created (`tests/unit/`, `tests/integration/`)
- [x] All transition tests passing

### Ready for Production Build
- [x] Database schema designed (`database/schema.sql`)
- [x] Kafka topics defined (`kafka_client.py:TOPICS`)
- [x] Channel handlers outlined (`channels/`)
- [x] Kubernetes resource requirements estimated (`k8s/`)
- [x] API endpoints listed (`api/router.py`)
