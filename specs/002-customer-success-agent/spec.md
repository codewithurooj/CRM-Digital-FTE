# Feature Specification: Customer Success AI Agent (Digital FTE)

**Feature Branch**: `002-customer-success-agent`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Build a 24/7 AI Customer Success agent that handles support across 3 channels (Web Form, Gmail, WhatsApp) with cross-channel identity, Kafka-based async processing, PostgreSQL CRM, Kubernetes deployment, and comprehensive monitoring."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Web Support Form Submission (Priority: P1)

A customer visits the TechCorp support page and fills out a web support form with their name, email, subject, category, priority, and message. Upon submission, the system validates all fields, creates a support ticket, and returns a confirmation with a ticket ID. The AI agent then processes the request asynchronously and sends a response to the customer's email within 5 minutes. The customer can check their ticket status using the ticket ID.

**Why this priority**: The Web Support Form is a REQUIRED deliverable worth 10 points. It is the only channel where the student must build both the frontend and backend. It also serves as the simplest channel to implement and test, forming the foundation for multi-channel architecture.

**Independent Test**: Can be fully tested by submitting a form via the React component, verifying ticket creation in the database, and confirming an acknowledgment response is returned — all without Gmail or WhatsApp dependencies.

**Acceptance Scenarios**:

1. **Given** a customer on the support page, **When** they fill out all required fields (name, email, subject, category, message) and click Submit, **Then** the system validates the input, creates a ticket, returns a ticket ID, and displays a success confirmation.
2. **Given** a submitted form with invalid data (email missing "@", message under 10 characters, name under 2 characters), **When** the form is submitted, **Then** the system rejects the submission with specific validation errors displayed inline.
3. **Given** a customer with a valid ticket ID, **When** they query the ticket status endpoint, **Then** the system returns the current ticket status and any agent responses.
4. **Given** the form is in a "submitting" state, **When** the submission is in progress, **Then** the submit button is disabled and shows a loading indicator to prevent duplicate submissions.

---

### User Story 2 - AI Agent Responds to Product Questions (Priority: P1)

A customer submits a product-related question through any channel. The AI agent searches the knowledge base for relevant documentation, creates a ticket to track the interaction, and generates a helpful response formatted appropriately for the originating channel. The agent follows a strict workflow: create ticket first, check customer history, search knowledge base, then send the response.

**Why this priority**: The AI agent is the core of the system, worth 10 points. Without a functioning agent, no channel delivers value. The agent's 5 tools (search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, send_response) form the backbone of every customer interaction.

**Independent Test**: Can be tested by sending a product question to the agent directly (bypassing channels) and verifying the response is accurate, the tool call order is correct, and a ticket was created.

**Acceptance Scenarios**:

1. **Given** a customer asks "How do I reset my password?", **When** the agent processes the message, **Then** it creates a ticket first, searches the knowledge base, and returns step-by-step instructions found in the product documentation.
2. **Given** a customer asks about a feature that exists in the documentation, **When** the agent processes the query, **Then** the response contains only verified facts from the knowledge base and no fabricated information.
3. **Given** a customer asks a follow-up question in the same conversation, **When** the agent processes it, **Then** the response acknowledges the prior context and builds upon the previous interaction.
4. **Given** the knowledge base returns no results after 2 search attempts, **When** the agent cannot find relevant information, **Then** it escalates to human support with context.

---

### User Story 3 - Agent Guardrails and Escalation (Priority: P1)

The AI agent enforces strict guardrails: it never discusses pricing, never promises unannounced features, and never processes refunds. When any of these triggers are detected, the agent immediately escalates to human support with a clear reason. Additional escalation triggers include legal threats, profanity, negative sentiment, and explicit requests for a human agent.

**Why this priority**: Guardrails are hard constraints. An agent that violates these (discussing pricing, promising features) would cause business harm. This is foundational to customer experience quality (10 points).

**Independent Test**: Can be tested by sending pricing, refund, and feature request queries to the agent and verifying escalation occurs in every case with the correct reason code.

**Acceptance Scenarios**:

1. **Given** a customer asks "How much does the enterprise plan cost?", **When** the agent processes the message, **Then** it immediately escalates with reason "pricing_inquiry" and never reveals any pricing information.
2. **Given** a customer requests "I need a refund for last month", **When** the agent processes the message, **Then** it immediately escalates with reason "refund_request" and does not attempt to process the refund.
3. **Given** a customer says "Will you add dark mode next quarter?", **When** the agent processes the message, **Then** it does not promise any unannounced features and only references capabilities documented in the knowledge base.
4. **Given** a customer says "I'm going to sue your company", **When** the agent detects legal language, **Then** it escalates to human support immediately.
5. **Given** a customer on WhatsApp types "human" or "agent", **When** the agent processes the message, **Then** it escalates to a human support representative.

---

### User Story 4 - Cross-Channel Customer Identity (Priority: P1)

A customer contacts support via email, then follows up via WhatsApp. The system identifies the customer across channels using their email, phone number, or other identifiers, and preserves the full conversation history. The agent acknowledges prior interactions regardless of the original channel.

**Why this priority**: Cross-channel continuity is worth 10 points and is central to the "unified CRM" value proposition. A customer should never have to repeat themselves when switching channels.

**Independent Test**: Can be tested by creating a customer via web form, then submitting a query via a different channel with the same email, and verifying the system links both interactions to a single customer record.

**Acceptance Scenarios**:

1. **Given** a customer with email "alice@example.com" submits via web form, **When** the same email sends an email via Gmail, **Then** both interactions are linked to the same customer record.
2. **Given** a customer previously contacted support via email, **When** they send a WhatsApp message from a phone number linked to their account, **Then** the agent says "I see you contacted us previously about [topic]" and has access to the full history.
3. **Given** a new customer contacts via WhatsApp with a phone number not in the system, **When** the system processes the message, **Then** a new customer record is created with the WhatsApp identifier for future matching.
4. **Given** a customer has interactions across all three channels, **When** the customer history is retrieved, **Then** it includes messages from email, WhatsApp, and web form in chronological order.

---

### User Story 5 - Channel-Appropriate Response Formatting (Priority: P2)

The agent adapts its response style and length based on the originating channel. Email responses are formal with greetings and signatures (up to 500 words). WhatsApp responses are concise and conversational (under 300 characters preferred, max 1600). Web form responses are semi-formal (up to 300 words). Long WhatsApp responses are automatically split into multiple messages at natural break points.

**Why this priority**: Channel-appropriate responses contribute to customer experience quality (10 points). Sending a 500-word email-style response on WhatsApp provides a poor user experience.

**Independent Test**: Can be tested by sending the same question ("How do I reset my password?") via each channel and verifying the response length, tone, and formatting differ appropriately.

**Acceptance Scenarios**:

1. **Given** a product question arrives via email, **When** the agent responds, **Then** the response includes a formal greeting ("Dear Customer"), detailed answer, and signature with ticket reference.
2. **Given** the same question arrives via WhatsApp, **When** the agent responds, **Then** the response is under 300 characters, conversational in tone, and ends with a prompt for more help.
3. **Given** a question arrives via the web form, **When** the agent responds, **Then** the response is semi-formal, includes actionable next steps, and is under 300 words.
4. **Given** an agent response exceeds 1600 characters for WhatsApp, **When** formatting for WhatsApp delivery, **Then** the response is split into multiple messages at natural sentence boundaries.

---

### User Story 6 - Asynchronous Message Processing via Kafka (Priority: P2)

When a message arrives from any channel (web form POST, Gmail webhook, WhatsApp webhook), the webhook handler publishes the normalized message to a Kafka topic and returns immediately (under 500ms). A separate worker pod consumes messages from Kafka, runs the AI agent, and routes responses back through the appropriate channel. Failed messages are sent to a dead-letter queue for human review.

**Why this priority**: Async processing via Kafka enables 24/7 scalability and prevents webhook timeouts. It is worth 5 points directly (Database & Kafka) and is essential for 24/7 readiness (10 points).

**Independent Test**: Can be tested by publishing a message to the Kafka topic and verifying a worker pod consumes it, processes it through the agent, and produces an outbound response event.

**Acceptance Scenarios**:

1. **Given** a web form submission arrives, **When** the FastAPI endpoint processes it, **Then** it publishes to `fte.tickets.incoming` and returns a ticket ID within 500ms.
2. **Given** a message is published to Kafka, **When** the worker pod consumes it, **Then** the agent processes the message, stores the response in the database, and sends the response via the correct channel.
3. **Given** the agent throws an error during processing, **When** the worker catches the error, **Then** it sends an apologetic response to the customer, publishes the failed message to the dead-letter queue, and logs the error.
4. **Given** multiple messages arrive simultaneously, **When** multiple worker pods are running, **Then** messages are distributed across workers for parallel processing.

---

### User Story 7 - Gmail Email Integration (Priority: P2)

Customers send support emails to TechCorp's Gmail address. Gmail push notifications (via Pub/Sub) trigger a webhook that extracts the email content, normalizes it into the unified message format, and publishes it to Kafka for agent processing. The agent's response is sent back as a Gmail reply in the same email thread.

**Why this priority**: Gmail is one of two external channel integrations (combined 10 points). It demonstrates the channel-agnostic architecture and provides the formal communication channel.

**Independent Test**: Can be tested by simulating a Gmail Pub/Sub notification to the webhook endpoint and verifying the message is parsed, published to Kafka, and a reply email is constructed correctly.

**Acceptance Scenarios**:

1. **Given** a customer sends an email to support@techcorp.com, **When** the Gmail Pub/Sub notification arrives, **Then** the webhook extracts the sender email, subject, and body, and publishes a normalized message to Kafka.
2. **Given** the agent generates a response to an email, **When** the response is delivered, **Then** it is sent as a reply in the same Gmail thread with proper formatting (greeting, signature, ticket reference).
3. **Given** the email sender's address matches an existing customer, **When** the system resolves the customer, **Then** it links the email to the existing customer record.

---

### User Story 8 - WhatsApp Integration via Twilio (Priority: P2)

Customers send WhatsApp messages to TechCorp's support number. Twilio's webhook delivers the message to a FastAPI endpoint, which validates the Twilio signature, normalizes the message, and publishes it to Kafka. The agent's response is sent back via the Twilio WhatsApp API. Customers can type "human" or "agent" to request escalation.

**Why this priority**: WhatsApp is the second external channel integration. It validates the channel-agnostic architecture with a very different message format (short, casual) compared to email.

**Independent Test**: Can be tested by simulating a Twilio webhook POST to the WhatsApp endpoint and verifying the message is validated, parsed, and published to Kafka.

**Acceptance Scenarios**:

1. **Given** a customer sends a WhatsApp message, **When** the Twilio webhook arrives, **Then** the system validates the Twilio signature, extracts the phone number and message body, and publishes to Kafka.
2. **Given** a webhook with an invalid Twilio signature, **When** validation fails, **Then** the endpoint returns HTTP 403 and does not process the message.
3. **Given** the agent generates a response for WhatsApp, **When** it is delivered, **Then** it is sent via the Twilio API as a WhatsApp reply to the customer's phone number.
4. **Given** a WhatsApp customer sends "human", **When** the agent processes the message, **Then** the conversation is escalated to human support.

---

### User Story 9 - Kubernetes Deployment for 24/7 Uptime (Priority: P2)

The entire system (API pods, worker pods, PostgreSQL, Kafka) runs on a Kubernetes cluster with auto-scaling, health checks, and graceful restarts. API pods scale based on CPU utilization (3 to 20 replicas). Worker pods scale independently (3 to 30 replicas). Liveness and readiness probes ensure unhealthy pods are restarted automatically.

**Why this priority**: Kubernetes deployment is worth 5 points directly and is essential for 24/7 readiness (10 points). The system must survive pod kills and scale under load.

**Independent Test**: Can be tested by deploying to minikube, killing random pods, and verifying the system recovers and continues processing messages without message loss.

**Acceptance Scenarios**:

1. **Given** the system is deployed on Kubernetes, **When** a health check request hits `/health`, **Then** it returns 200 with status of all channels and components.
2. **Given** a worker pod is killed, **When** Kubernetes detects the pod is unhealthy, **Then** it restarts the pod and the worker resumes processing from Kafka's last committed offset (no message loss).
3. **Given** CPU utilization exceeds 70%, **When** the HPA evaluates scaling, **Then** additional pods are spawned (up to maxReplicas) and load is distributed.
4. **Given** secrets (API keys, credentials), **When** deployed to Kubernetes, **Then** they are stored in Kubernetes Secrets and injected as environment variables — never hardcoded.

---

### User Story 10 - Monitoring and Channel Metrics (Priority: P3)

Operations teams can view real-time metrics broken down by channel: total conversations, average sentiment, escalation count, response latency, and message volume. Alerts fire when response latency exceeds 3 seconds or escalation rate exceeds 25%. All metrics are persisted for historical reporting.

**Why this priority**: Monitoring is worth 5 points. It demonstrates operational readiness and supports the 24/7 reliability narrative.

**Independent Test**: Can be tested by processing messages through each channel and querying the `/metrics/channels` endpoint to verify per-channel breakdowns are accurate.

**Acceptance Scenarios**:

1. **Given** messages have been processed across all channels, **When** an operator queries `/metrics/channels`, **Then** the response shows conversation counts, sentiment averages, and escalation counts per channel for the last 24 hours.
2. **Given** response latency exceeds 3 seconds, **When** the metrics collector evaluates thresholds, **Then** an alert event is published for operations review.
3. **Given** per-channel metrics are collected, **When** historical data is queried, **Then** trends over time are available for each channel.

---

### User Story 11 - Incubation Discovery and MCP Server (Priority: P2)

During the incubation phase, the developer uses Claude Code as an Agent Factory to explore sample tickets, discover patterns across channels, and prototype the core interaction loop. The discoveries are documented in a discovery log. An MCP server exposes 5 tools (search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, send_response) as reusable capabilities that are later transformed into OpenAI SDK `@function_tool` definitions.

**Why this priority**: Incubation quality is worth 10 points. The discovery log, MCP server, and documented patterns demonstrate the evolution from general agent to custom agent.

**Independent Test**: Can be tested by verifying the MCP server exposes all 5 tools, the discovery log documents at least 10 patterns, and the transition from MCP to `@function_tool` is documented.

**Acceptance Scenarios**:

1. **Given** the sample tickets in `context/sample-tickets.json`, **When** the developer analyzes them during incubation, **Then** a discovery log documents patterns per channel (email tends to be longer, WhatsApp is more casual, web form has structured categories).
2. **Given** the MCP server is running, **When** each of the 5 tools is invoked, **Then** it returns a valid response according to its tool definition.
3. **Given** the incubation phase is complete, **When** the transition to production begins, **Then** each MCP tool maps to a corresponding `@function_tool` with added input validation, error handling, and database integration.

---

### User Story 12 - Innovation: Sentiment-Aware Routing and Learning (Priority: P3)

The system analyzes customer sentiment on every message and uses it to make intelligent routing decisions. Conversations trending negative are automatically prioritized and escalated sooner. Resolved tickets are analyzed to improve the knowledge base over time, enabling the agent to learn from successful resolutions. A daily digest summarizes customer sentiment, top issues, and resolution rates by channel.

**Why this priority**: Innovation is worth 10 points. Sentiment-aware routing and learning from resolved tickets go beyond the baseline requirements and demonstrate advanced AI agent capabilities.

**Independent Test**: Can be tested by sending messages with varying sentiment levels and verifying that negative-sentiment conversations trigger earlier escalation and priority bumps.

**Acceptance Scenarios**:

1. **Given** a customer's sentiment drops below 0.3 during a conversation, **When** the sentiment is evaluated, **Then** the conversation is automatically escalated to human support.
2. **Given** tickets are resolved throughout the day, **When** the daily digest runs, **Then** it summarizes top issues, average sentiment, resolution rates, and response times per channel.
3. **Given** a ticket was successfully resolved with a novel solution, **When** the learning pipeline processes it, **Then** the knowledge base is updated with the new resolution pattern for future queries.

---

### Edge Cases

- What happens when a customer sends an empty message via any channel? The system returns a friendly prompt asking for details and does not crash.
- What happens when the knowledge base returns zero results? The agent attempts one more refined search, and if still empty, escalates with context.
- What happens when a WhatsApp message contains media (images, documents)? The system acknowledges the attachment but informs the customer that only text messages are currently supported.
- What happens when Kafka is temporarily unavailable? The webhook handler retries with exponential backoff, and the message is queued in memory with a maximum retry window.
- What happens when a customer contacts from a new phone number but uses a previously-seen email in their WhatsApp profile? The system merges the identifiers into the existing customer record.
- What happens when the agent receives a message in a language other than English? The agent responds in English but acknowledges the language and suggests contacting support in the customer's preferred language.
- What happens when a customer sends multiple rapid messages via WhatsApp? The system batches them into a single context window for the agent to process together.
- What happens when the OpenAI API is unavailable? The system sends a fallback "We're experiencing high demand" message and escalates to human support.
- What happens when a webhook endpoint receives a malformed payload? The endpoint returns a 400 error with a descriptive message and does not publish to Kafka.
- What happens when a customer's ticket is already resolved but they send a follow-up? The system reopens or creates a new conversation linked to the original ticket.

## Requirements *(mandatory)*

### Functional Requirements

**Web Support Form (REQUIRED)**
- **FR-001**: System MUST provide a React/Next.js web support form with fields for name, email, subject, category, priority, and message.
- **FR-002**: System MUST validate form inputs client-side and server-side: name (min 2 chars), email (valid format), subject (min 5 chars), message (min 10 chars), category (from allowed list).
- **FR-003**: System MUST return a unique ticket ID upon successful form submission.
- **FR-004**: System MUST provide a ticket status endpoint where customers can check the progress of their submission by ticket ID.
- **FR-005**: System MUST display loading state during submission and prevent duplicate submissions.

**AI Agent Core**
- **FR-006**: System MUST implement an AI agent using the OpenAI Agents SDK with GPT-4o as the underlying model.
- **FR-007**: System MUST provide 5 agent tools: search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, and send_response.
- **FR-008**: System MUST enforce a strict tool execution order: create_ticket first, then get_customer_history, then search_knowledge_base (if needed), then send_response last.
- **FR-009**: System MUST search the knowledge base using vector similarity (pgvector) for semantic matching of customer queries.
- **FR-010**: System MUST create a ticket BEFORE generating any response to the customer.

**Agent Guardrails**
- **FR-011**: System MUST immediately escalate any pricing-related inquiry without revealing pricing information.
- **FR-012**: System MUST immediately escalate any refund request without attempting to process the refund.
- **FR-013**: System MUST never promise features not present in the knowledge base documentation.
- **FR-014**: System MUST escalate when the customer uses legal threat language ("lawyer", "legal", "sue", "attorney").
- **FR-015**: System MUST escalate when customer sentiment drops below 0.3.
- **FR-016**: System MUST escalate when a WhatsApp customer sends "human", "agent", or "representative".
- **FR-017**: System MUST escalate when relevant information cannot be found after 2 search attempts.

**Multi-Channel Support**
- **FR-018**: System MUST accept incoming emails via Gmail API webhook (Pub/Sub push notifications).
- **FR-019**: System MUST accept incoming WhatsApp messages via Twilio webhook with signature validation.
- **FR-020**: System MUST reply to emails in the same Gmail thread.
- **FR-021**: System MUST reply to WhatsApp messages via the Twilio API.
- **FR-022**: System MUST reply to web form submissions via stored response (API-retrievable) and email notification.

**Cross-Channel Identity**
- **FR-023**: System MUST identify the same customer across channels using email address as the primary identifier.
- **FR-024**: System MUST link WhatsApp phone numbers to customer records via a customer_identifiers table.
- **FR-025**: System MUST provide customer history spanning all channels when the agent retrieves context.
- **FR-026**: System MUST create a new customer record when no matching identifier exists in the system.

**Channel Response Formatting**
- **FR-027**: System MUST format email responses with formal greeting, detailed body, and professional signature (max 500 words).
- **FR-028**: System MUST format WhatsApp responses concisely (preferred under 300 characters, max 1600) with conversational tone.
- **FR-029**: System MUST format web form responses semi-formally (max 300 words) with clear next steps.
- **FR-030**: System MUST split WhatsApp responses exceeding 1600 characters into multiple messages at natural sentence boundaries.

**Infrastructure**
- **FR-031**: System MUST use Kafka topics to decouple channel intake from agent processing, with webhook handlers returning within 500ms.
- **FR-032**: System MUST persist all state (customers, conversations, messages, tickets) in PostgreSQL.
- **FR-033**: System MUST store knowledge base entries with vector embeddings (1536-dimensional) for semantic search.
- **FR-034**: System MUST publish failed processing attempts to a dead-letter queue topic for human review.
- **FR-035**: System MUST send an apologetic fallback message to the customer's channel when agent processing fails.

**Graceful Failure**
- **FR-036**: System MUST never surface raw error messages or stack traces to customers.
- **FR-037**: System MUST escalate to human support as the ultimate fallback for any unrecoverable error.

**Monitoring**
- **FR-038**: System MUST expose a `/health` endpoint returning the status of all components.
- **FR-039**: System MUST expose a `/metrics/channels` endpoint with per-channel conversation counts, sentiment averages, and escalation counts.
- **FR-040**: System MUST record agent performance metrics (latency, tool call counts, escalation rates) in the database.

**Kubernetes Deployment**
- **FR-041**: System MUST deploy via Kubernetes manifests with separate deployments for API pods and worker pods.
- **FR-042**: System MUST configure liveness and readiness probes on all pods.
- **FR-043**: System MUST auto-scale API pods (3-20 replicas) and worker pods (3-30 replicas) based on CPU utilization.
- **FR-044**: System MUST store all secrets in Kubernetes Secrets, never in source code or configuration files.

**Documentation and Discovery**
- **FR-045**: System MUST include a discovery log documenting patterns found during incubation.
- **FR-046**: System MUST include an MCP server with 5 tools as the incubation deliverable.
- **FR-047**: System MUST include deployment documentation and API reference.

### Key Entities

- **Customer**: A unified record representing a person who contacts support, with email and phone attributes. A customer may have multiple identifiers across channels but is represented as a single entity.
- **Customer Identifier**: A mapping between a customer and their channel-specific identifier (email address, phone number, WhatsApp ID). Enables cross-channel matching.
- **Conversation**: A thread of messages between a customer and the agent, with a starting channel, status (active/closed/escalated), sentiment score, and optional resolution type.
- **Message**: An individual inbound or outbound message within a conversation, tagged with channel, direction, role (customer/agent/system), delivery status, and processing latency.
- **Ticket**: A support ticket created for every customer interaction, with category, priority, status lifecycle (open → processing → resolved/escalated), source channel, and resolution notes.
- **Knowledge Base Entry**: A piece of product documentation with a title, content, category, and vector embedding for semantic search.
- **Channel Configuration**: Per-channel settings including enabled status, response templates, maximum response lengths, and API configuration references.
- **Agent Metric**: A time-series record of agent performance data (response latency, escalation rate, sentiment scores) optionally segmented by channel.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Customers can submit a support request via the web form and receive a ticket ID confirmation in under 3 seconds.
- **SC-002**: The AI agent generates and delivers a response to customer inquiries within 30 seconds end-to-end (across all channels).
- **SC-003**: 95% or more of customers contacting via multiple channels are correctly identified as the same person.
- **SC-004**: The system maintains greater than 99.9% uptime over a 24-hour continuous operation test.
- **SC-005**: Pricing, refund, and legal inquiries are escalated 100% of the time — no guardrail violation escapes to the customer.
- **SC-006**: Escalation rate for routine queries remains below 25%.
- **SC-007**: The system handles 100+ web form submissions, 50+ emails, and 50+ WhatsApp messages over a 24-hour test period without message loss.
- **SC-008**: Response formatting passes channel-appropriateness validation: email responses include greeting and signature, WhatsApp responses are under 300 characters preferred, web responses are semi-formal.
- **SC-009**: The system survives random pod kills (every 2 hours during the 24-hour test) and recovers automatically with no manual intervention.
- **SC-010**: All test suites pass with minimum 80% code coverage.
- **SC-011**: The web support form validates input correctly and prevents invalid submissions 100% of the time.
- **SC-012**: Agent knowledge base accuracy exceeds 85% on a standardized test set of customer queries.

## Assumptions

- **A-001**: TechCorp is a fictional SaaS company whose product documentation, company profile, sample tickets, and brand voice are provided in the `context/` folder.
- **A-002**: The Gmail integration uses the Gmail API sandbox with OAuth2 credentials. Production Gmail accounts are not required.
- **A-003**: The WhatsApp integration uses the Twilio WhatsApp Sandbox. A production WhatsApp Business account is not required.
- **A-004**: The knowledge base is seeded from `context/product-docs.md` with pre-computed vector embeddings using OpenAI's embedding model.
- **A-005**: PostgreSQL 16 with the pgvector extension is the only database required. No external CRM (Salesforce, HubSpot) is needed.
- **A-006**: Kubernetes deployment targets minikube for local development and demonstration.
- **A-007**: The web support form is a standalone, embeddable React component — not a full website.
- **A-008**: Data retention follows standard SaaS practices (indefinite for support interactions, 90 days for metrics).
- **A-009**: The system operates in English only. Non-English messages receive an English response acknowledging the language barrier.
- **A-010**: OpenAI GPT-4o is the LLM used for the agent. Cost is estimated at under $1,000/year based on projected message volume.

## Scope Boundaries

### In Scope
- Web support form (React/Next.js) with validation and status checking
- AI agent with OpenAI Agents SDK and 5 function tools
- Gmail integration (inbound via Pub/Sub, outbound via Gmail API)
- WhatsApp integration (inbound/outbound via Twilio)
- PostgreSQL CRM (customers, conversations, messages, tickets, knowledge base)
- Kafka event streaming with dead-letter queue
- Cross-channel customer identity matching
- Channel-specific response formatting
- Kubernetes deployment with auto-scaling
- Monitoring and channel metrics
- Incubation deliverables (MCP server, discovery log, agent skills)
- TDD with 80% coverage gate

### Out of Scope
- Full website beyond the support form component
- External CRM integration (Salesforce, HubSpot)
- Production WhatsApp Business account
- Multi-language support (agent operates in English only)
- Payment processing or billing system
- User authentication for the support portal (submissions are anonymous with email)
- Mobile app
- Admin dashboard for human agents
- SMS channel (only WhatsApp via Twilio)
- File attachment processing (images, PDFs in messages)
