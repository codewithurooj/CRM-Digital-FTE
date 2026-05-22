# Customer Success FTE Specification

> **Full specification**: `specs/002-customer-success-agent/spec.md`  
> This file is the top-level crystallization document required by Hackathon 5.

## Purpose

Handle routine customer support queries with speed and consistency across multiple channels, replacing a $75,000/year human support agent with an AI Digital FTE costing <$1,000/year.

## Supported Channels

| Channel | Identifier | Response Style | Max Length |
|---------|------------|----------------|------------|
| Email (Gmail) | Email address | Formal, detailed | 500 words |
| WhatsApp (Twilio) | Phone number | Conversational, concise | 1,600 chars |
| Web Form | Email address | Semi-formal | 300 words |

## Scope

### In Scope
- Product feature questions
- How-to guidance
- Bug report intake
- Feedback collection
- Cross-channel conversation continuity (same customer identified across all 3 channels)

### Out of Scope → Escalate Immediately
- Pricing negotiations (`pricing_inquiry`)
- Refund requests (`refund_request`)
- Legal/compliance questions (`legal_threat`)
- Abusive language (`abusive_language`)
- Angry customers (sentiment < 0.3 → `negative_sentiment`)
- Explicit human request (`human_request`)

## Tools

| Tool | Purpose | Constraints |
|------|---------|-------------|
| `search_knowledge_base` | pgvector semantic search on product docs | Max 5 results; uses OpenAI `text-embedding-3-small` |
| `create_ticket` | Log every interaction — MUST be called first | Required before any response |
| `get_customer_history` | Retrieve prior messages across ALL channels | Default 10 messages |
| `escalate_to_human` | Hand off to human agent | Must include reason code |
| `send_response` | Format and store reply per channel | Enforces channel length limits |

## Required Workflow (Strict Order)

1. `create_ticket` — always first
2. `get_customer_history` — check prior context
3. `search_knowledge_base` — for product questions
4. `send_response` or `escalate_to_human` — always last

## Guardrails (Hard Constraints)

- NEVER discuss pricing → escalate with `pricing_inquiry`
- NEVER promise features not in documentation
- NEVER process refunds → escalate with `refund_request`
- NEVER respond without calling `send_response` tool
- ALWAYS create ticket before responding
- ALWAYS check sentiment before closing

## Performance Requirements

| Metric | Target |
|--------|--------|
| Response time (processing) | < 3 seconds |
| Response time (delivery) | < 30 seconds |
| Escalation rate | < 20% |
| Cross-channel identification accuracy | > 95% |
| Knowledge base hit rate | > 60% of queries |

## Architecture

```
Gmail Webhook ──┐
WhatsApp Hook ──┼──→ Kafka (fte.tickets.incoming) ──→ Worker Pod ──→ Agent (GPT-4o) ──→ Response
Web Form POST ──┘                                      (consumer)                       (via channel)
```

State: PostgreSQL 16 with pgvector  
Deployment: Kubernetes (minikube) with HPA auto-scaling  
Secrets: Environment variables only — no hardcoded credentials
