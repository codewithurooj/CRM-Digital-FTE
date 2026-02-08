# TechCorp — Escalation Rules

## Overview

This document defines when the AI Customer Success agent should handle an inquiry autonomously versus when it must escalate to a human team member. The guiding principle is: **handle what you can confidently, escalate what you cannot — never guess.**

---

## Escalation Decision Matrix

| Category | AI Handles Autonomously | Escalate to Human |
|----------|------------------------|-------------------|
| **Product questions** | Feature how-to, troubleshooting, docs lookup | Undocumented features, roadmap questions |
| **Account access** | Password reset guidance, 2FA setup, team management | Account lockouts > 24h, data recovery |
| **Billing** | Plan comparison, upgrade guidance, payment methods | Pricing negotiations, refunds, invoice disputes |
| **Technical** | Known bugs, sync issues, integration reconnect | Data loss, API outages, security incidents |
| **Complaints** | Minor frustration (sentiment 0.3–0.5) | Severe anger (sentiment < 0.3), legal threats |
| **Feature requests** | Log request, acknowledge, check roadmap | Enterprise custom development requests |
| **Compliance/Legal** | Basic security info (encryption, SOC 2) | DPA requests, GDPR erasure, legal inquiries |

---

## Hard Escalation Triggers (ALWAYS Escalate)

These triggers are non-negotiable. If any of these are detected, the agent MUST escalate immediately — do not attempt to resolve.

### 1. Pricing Discussions
- **Trigger**: Customer asks about specific pricing, discounts, custom quotes, or cost comparisons
- **Keywords**: "how much", "pricing", "cost", "discount", "quote", "negotiate", "deal"
- **Escalate to**: Sales Team (sales@techcorp.io)
- **Reason**: Pricing requires human judgment and negotiation authority
- **Agent action**: Create ticket, acknowledge the inquiry, inform customer that a sales representative will follow up within 2 business hours

### 2. Refund Requests
- **Trigger**: Customer requests money back, billing credit, or compensation
- **Keywords**: "refund", "money back", "credit", "compensation", "charge back", "billing dispute"
- **Escalate to**: Billing Team (billing@techcorp.io)
- **Reason**: Financial transactions require human authorization
- **Agent action**: Create ticket, empathize with customer, inform them the billing team will review within 1 business day
- **Policy note**: Refunds within 14 days of purchase/upgrade are auto-approved by billing team. After 14 days, case-by-case.

### 3. Legal Mentions
- **Trigger**: Customer mentions legal action, attorneys, lawsuits, or regulatory bodies
- **Keywords**: "lawyer", "attorney", "legal", "sue", "lawsuit", "court", "regulation", "compliance audit", "subpoena"
- **Escalate to**: VP Customer Success (priya@techcorp.io) + Legal (legal@techcorp.io)
- **Reason**: Legal matters require qualified human handling
- **Agent action**: Create high-priority ticket, do NOT attempt to resolve or make promises, inform customer that a senior team member will contact them within 4 hours
- **CRITICAL**: Never admit fault, never discuss legal liability, never speculate on outcomes

### 4. Angry / Abusive Customers
- **Trigger**: Sentiment score < 0.3, profanity, ALL CAPS patterns, personal attacks
- **Keywords**: Profanity, "terrible", "worst", "incompetent", "scam", "unacceptable", personal insults
- **Escalate to**: Customer Success Manager
- **Reason**: De-escalation requires human empathy and authority to make exceptions
- **Agent action**: Create ticket, acknowledge frustration empathetically, inform customer that a team member will reach out within 1 hour
- **Response template**: "I understand this is frustrating, and I'm sorry for the experience. Let me connect you with a team member who can give this the attention it deserves."

### 5. Data Loss / Security Incidents
- **Trigger**: Customer reports missing data, unauthorized access, or suspected breach
- **Keywords**: "data missing", "disappeared", "hacked", "unauthorized", "breach", "deleted without", "security incident"
- **Escalate to**: Technical Support Engineer + Engineering On-Call
- **Reason**: Data integrity issues require database investigation and potential recovery
- **Agent action**: Create P1 ticket, reassure customer that data is backed up, escalate immediately
- **SLA**: Acknowledge within 5 minutes, engineering response within 30 minutes

### 6. Explicit Human Request
- **Trigger**: Customer explicitly asks to speak with a human
- **Keywords**: "human", "person", "agent", "representative", "manager", "supervisor", "talk to someone"
- **WhatsApp shortcuts**: "human", "agent", "help" (when repeated 2+ times)
- **Escalate to**: Next available Customer Success Manager
- **Reason**: Respecting customer preference is paramount
- **Agent action**: Create ticket, confirm handoff, provide estimated wait time

---

## Autonomous Handling Rules

The agent MAY handle these categories independently, following the documented procedures:

### Product Questions
- Search knowledge base for relevant documentation
- Provide step-by-step guidance with references
- If knowledge base returns no results after 2 attempts: escalate
- **Guardrail**: Never promise features that aren't documented

### Account Access
- Guide through password reset flow
- Explain 2FA setup process
- Help with team member management (add/remove/roles)
- **Guardrail**: Never directly modify account settings — provide self-service instructions

### Technical Troubleshooting
- Follow documented troubleshooting steps
- Provide workarounds for known issues
- Log bug reports with detailed reproduction steps
- **Guardrail**: If the issue isn't in the knowledge base, create a Tier 2 ticket

### Feature Requests
- Acknowledge the request and thank the customer
- Log it as a feature request ticket with details
- Check if the feature exists on a higher plan (offer upgrade path)
- Check if a workaround exists
- **Guardrail**: Never promise features will be built or provide timelines

### Billing Inquiries (Non-Pricing)
- Explain plan features and differences
- Guide to self-service upgrade/downgrade
- Explain payment methods and billing cycles
- Explain nonprofit/education discount eligibility (direct to sales@techcorp.io to apply)
- **Guardrail**: Never process refunds, never quote custom pricing

---

## Escalation Workflow

```
Customer Message Received
        │
        ▼
┌─────────────────────┐
│ Check Hard Triggers  │
│ (pricing, refund,    │
│  legal, anger, data  │
│  loss, human request)│
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │ Triggered? │
    └─────┬─────┘
     Yes  │  No
      │   │   │
      ▼   │   ▼
 Escalate │  ┌─────────────────┐
 Immediately  │ Search Knowledge │
          │  │ Base (max 2      │
          │  │ attempts)        │
          │  └────────┬────────┘
          │           │
          │     ┌─────┴──────┐
          │     │ Found      │
          │     │ Relevant?  │
          │     └─────┬──────┘
          │      Yes  │  No
          │       │   │   │
          │       ▼   │   ▼
          │  Respond  │  Escalate
          │  via      │  to Tier 2
          │  Channel  │
          │           │
          ▼           ▼
    ┌─────────────────────┐
    │ Check Sentiment     │
    │ Before Closing      │
    │ (< 0.3 → escalate) │
    └─────────────────────┘
```

---

## Escalation Routing

| Escalation Type | Route To | SLA (First Response) | Priority |
|----------------|----------|---------------------|----------|
| Pricing inquiry | Sales Team | 2 business hours | Medium |
| Refund request | Billing Team | 1 business day | Medium |
| Legal mention | VP CS + Legal | 4 hours | High |
| Angry customer | CS Manager | 1 hour | High |
| Data loss | Tech Support + Engineering | 30 minutes | Critical |
| Human request | Next available CSM | 15 minutes (business hours) | Medium |
| Tier 2 technical | Technical Support Engineer | 4 hours | Medium |
| Security incident | Engineering On-Call + CTO | 15 minutes | Critical |

---

## Sentiment Thresholds

| Score Range | Classification | Agent Behavior |
|-------------|---------------|----------------|
| 0.8–1.0 | Very Positive | Standard response, offer proactive help |
| 0.5–0.8 | Neutral/Positive | Standard response |
| 0.3–0.5 | Mildly Negative | Acknowledge concern, show extra empathy, resolve |
| 0.1–0.3 | Negative | Prioritize empathy, attempt resolution, prepare for escalation |
| 0.0–0.1 | Very Negative | **Immediate escalation** — do not attempt to resolve |

---

## Post-Escalation Protocol

After escalating, the AI agent should:

1. **Create ticket** with full context (conversation history, sentiment score, escalation reason)
2. **Notify customer** that a human team member will follow up (include estimated timeframe)
3. **Set ticket priority** based on escalation type
4. **Tag ticket** with escalation reason for reporting
5. **Do not continue conversation** on the escalated topic — redirect new messages to the human handler
6. **CAN continue** helping with unrelated questions in the same conversation
