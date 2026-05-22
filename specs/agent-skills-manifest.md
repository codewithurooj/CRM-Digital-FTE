# Agent Skills Manifest — Customer Success FTE

> **Agent**: TechCorp Customer Success Agent  
> **SDK**: OpenAI Agents SDK (`@function_tool`)  
> **Created**: 2026-05-18

This manifest defines the 5 reusable skills the agent can invoke. Each skill maps to one or more `@function_tool` functions in `production/agent/tools.py`.

---

## Skill 1: Knowledge Retrieval

**Tool**: `search_knowledge_base`  
**When to use**: Customer asks product questions — features, how-to, API usage, troubleshooting  
**Inputs**:
- `query` (str) — the customer's question or search terms
- `category` (str, optional) — filter: `account`, `billing`, `technical`, `how_to`, `troubleshooting`

**Outputs**: Up to 5 ranked documentation snippets with title, content (first 500 chars), category, and similarity score  
**Implementation**: pgvector cosine similarity using OpenAI `text-embedding-3-small` embeddings; falls back to category search if embedding API is unavailable  
**Constraints**: Max 5 results; search attempted twice before escalating on no match

---

## Skill 2: Sentiment Analysis

**Implementation**: `production/workers/message_processor.py:score_sentiment()`  
**When to use**: On every inbound customer message before routing to agent  
**Inputs**: `message` (str) — raw customer message text  
**Outputs**: `sentiment_score` (float 0.0–1.0) — 0.0 is very negative, 1.0 is very positive  
**Logic**: Keyword-based scoring (fast, deterministic) — negative word hits decrease score, positive word hits increase score  
**Escalation trigger**: score < 0.3 → `negative_sentiment` escalation

---

## Skill 3: Escalation Decision

**Tool**: `escalate_to_human`  
**When to use**: After guardrail check or when agent determines human intervention is required  
**Inputs**:
- `customer_id` (str)
- `ticket_id` (str)
- `reason` (str) — one of: `pricing_inquiry`, `refund_request`, `legal_threat`, `human_request`, `data_security`, `abusive_language`, `negative_sentiment`, `no_kb_match`
- `conversation_id` (str, optional)
- `notes` (str, optional) — context for the human agent

**Outputs**: Escalation confirmation with reason and status  
**Side effects**: Updates ticket status to `escalated`, updates conversation status, records escalation metric in `agent_metrics`  
**Hard triggers** (checked before agent runs in `check_guardrails()`):
- "pricing", "how much", "cost", "plan price"
- "refund", "money back", "charge"
- "lawyer", "legal", "sue", "attorney"
- "cancel", "cancellation"
- profanity keywords
- sentiment_score < 0.3

---

## Skill 4: Channel Adaptation

**Tool**: `send_response` / `production/agent/formatters.py:format_response()`  
**When to use**: Before sending any response — formats content for the originating channel  
**Inputs**:
- `response_text` (str) — raw agent response
- `channel` (str) — `email`, `whatsapp`, or `web_form`
- `customer_name` (str) — for personalized greeting
- `ticket_number` (str) — appended to response

**Outputs**: Channel-formatted response string

| Channel | Format | Length Limit |
|---------|--------|-------------|
| `email` | `Hi {name},\n\n{body}\n\nTicket: {num}\n\nBest regards, TechCorp Support` | 500 words |
| `whatsapp` | `{body}\n\nTicket: {num}` (concise, no formal greeting) | 1,600 chars |
| `web_form` | `Hi {name},\n\n{body}\n\nTicket: {num}` (semi-formal) | 300 words |

---

## Skill 5: Customer Identification

**Implementation**: `production/workers/message_processor.py:MessageProcessor.resolve_customer()`  
**When to use**: On every incoming message before conversation lookup  
**Inputs**: Inbound message dict with `customer_identifier` and `identifier_type` (`email`, `phone`, `user_id`)  
**Outputs**: Unified `customer_id` (UUID) — existing or newly created  
**Logic**:
1. Look up `customer_identifiers` by `(identifier_type, identifier_value)`
2. If found → return linked `customer_id`
3. If not found → create new `customers` row + `customer_identifiers` row
4. Email takes precedence over phone for identity merging

**Cross-channel matching**: A customer who emails from `alice@example.com` and later WhatsApps from `+15551234567` will be merged once an agent or admin links the phone to the email in `customer_identifiers`.
