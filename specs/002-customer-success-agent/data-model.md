# Data Model: PostgreSQL Schema — CRM Digital FTE

**Branch**: `002-customer-success-agent` | **Date**: 2026-02-08
**Database**: PostgreSQL 16 + pgvector extension
**Driver**: asyncpg (raw SQL, no ORM)

## Entity Relationship Overview

```
customers (1) ──── (N) customer_identifiers
    │
    ├── (1) ──── (N) conversations
    │                    │
    │                    └── (1) ──── (N) messages
    │
    └── (1) ──── (N) tickets
                         │
                         └── (N) ──── (1) conversations

knowledge_base          (standalone, vector-indexed)
channel_configs         (standalone, per-channel settings)
agent_metrics           (standalone, time-series)
```

**Key relationships**:
- A **customer** has many **identifiers** (email, phone, WhatsApp ID) for cross-channel matching
- A **customer** has many **conversations**, each tied to an originating channel
- A **conversation** has many **messages** (inbound + outbound, tagged by channel)
- A **customer** has many **tickets**, each optionally linked to a conversation
- **knowledge_base** entries are searched via pgvector similarity (no FK relationships)
- **channel_configs** stores per-channel settings (tone, max length, templates)
- **agent_metrics** is a time-series table for performance tracking

---

## Schema DDL

```sql
-- =============================================================================
-- CRM Digital FTE — PostgreSQL Schema
-- Version: 1.0.0
-- Requires: PostgreSQL 16+, pgvector extension
-- =============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- =============================================================================
-- 1. CUSTOMERS — Unified customer records
-- =============================================================================
CREATE TABLE customers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    name            VARCHAR(255),
    phone           VARCHAR(50),
    company         VARCHAR(255),
    plan            VARCHAR(50) DEFAULT 'free'
                    CHECK (plan IN ('free', 'starter', 'professional', 'enterprise')),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone) WHERE phone IS NOT NULL;

-- =============================================================================
-- 2. CUSTOMER_IDENTIFIERS — Cross-channel identity matching
-- =============================================================================
CREATE TABLE customer_identifiers (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type     VARCHAR(50) NOT NULL
                        CHECK (identifier_type IN ('email', 'phone', 'whatsapp')),
    identifier_value    VARCHAR(255) NOT NULL,
    channel             VARCHAR(50) NOT NULL
                        CHECK (channel IN ('email', 'whatsapp', 'web_form')),
    verified            BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

CREATE INDEX idx_identifiers_lookup ON customer_identifiers(identifier_type, identifier_value);
CREATE INDEX idx_identifiers_customer ON customer_identifiers(customer_id);

-- =============================================================================
-- 3. CONVERSATIONS — Conversation threads with channel tracking
-- =============================================================================
CREATE TABLE conversations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES customers(id),
    channel             VARCHAR(50) NOT NULL
                        CHECK (channel IN ('email', 'whatsapp', 'web_form')),
    status              VARCHAR(50) DEFAULT 'active'
                        CHECK (status IN ('active', 'closed', 'escalated')),
    sentiment_score     FLOAT DEFAULT 0.5,
    resolution_type     VARCHAR(50)
                        CHECK (resolution_type IS NULL OR
                               resolution_type IN ('resolved', 'escalated', 'abandoned')),
    escalation_reason   VARCHAR(255),
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    closed_at           TIMESTAMPTZ
);

CREATE INDEX idx_conversations_customer ON conversations(customer_id, status);
CREATE INDEX idx_conversations_channel ON conversations(channel, status);
CREATE INDEX idx_conversations_created ON conversations(created_at);

-- =============================================================================
-- 4. MESSAGES — All messages (inbound + outbound) with channel metadata
-- =============================================================================
CREATE TABLE messages (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id         UUID NOT NULL REFERENCES conversations(id),
    customer_id             UUID NOT NULL REFERENCES customers(id),
    channel                 VARCHAR(50) NOT NULL
                            CHECK (channel IN ('email', 'whatsapp', 'web_form')),
    direction               VARCHAR(10) NOT NULL
                            CHECK (direction IN ('inbound', 'outbound')),
    role                    VARCHAR(20) NOT NULL
                            CHECK (role IN ('customer', 'agent', 'system')),
    content                 TEXT NOT NULL,
    content_type            VARCHAR(50) DEFAULT 'text'
                            CHECK (content_type IN ('text', 'html', 'attachment_notice')),
    delivery_status         VARCHAR(50) DEFAULT 'pending'
                            CHECK (delivery_status IN ('pending', 'delivered', 'failed', 'read')),
    processing_latency_ms   INTEGER,
    metadata                JSONB DEFAULT '{}',
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_customer ON messages(customer_id, created_at);
CREATE INDEX idx_messages_channel ON messages(channel, created_at);

-- =============================================================================
-- 5. TICKETS — Support tickets with status lifecycle
-- =============================================================================

-- Sequence for human-readable ticket numbers
CREATE SEQUENCE ticket_number_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE tickets (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_number       VARCHAR(20) UNIQUE NOT NULL,
    conversation_id     UUID REFERENCES conversations(id),
    customer_id         UUID NOT NULL REFERENCES customers(id),
    subject             VARCHAR(500) NOT NULL,
    category            VARCHAR(100) NOT NULL
                        CHECK (category IN ('account_access', 'billing', 'technical',
                                           'how_to', 'feature_request', 'complaint')),
    priority            VARCHAR(20) DEFAULT 'medium'
                        CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status              VARCHAR(50) DEFAULT 'open'
                        CHECK (status IN ('open', 'processing', 'waiting',
                                         'resolved', 'escalated', 'closed')),
    source_channel      VARCHAR(50) NOT NULL
                        CHECK (source_channel IN ('email', 'whatsapp', 'web_form')),
    assigned_to         VARCHAR(255),
    escalation_reason   VARCHAR(255),
    resolution_notes    TEXT,
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    resolved_at         TIMESTAMPTZ
);

CREATE INDEX idx_tickets_customer ON tickets(customer_id, status);
CREATE INDEX idx_tickets_status ON tickets(status, priority);
CREATE INDEX idx_tickets_channel ON tickets(source_channel, created_at);
CREATE INDEX idx_tickets_number ON tickets(ticket_number);

-- Auto-generate TKT-XXXX ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ticket_number := 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ticket_number
    BEFORE INSERT ON tickets
    FOR EACH ROW
    WHEN (NEW.ticket_number IS NULL OR NEW.ticket_number = '')
    EXECUTE FUNCTION generate_ticket_number();

-- =============================================================================
-- 6. KNOWLEDGE_BASE — Product docs with pgvector embeddings
-- =============================================================================
CREATE TABLE knowledge_base (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(500) NOT NULL,
    content         TEXT NOT NULL,
    category        VARCHAR(100) NOT NULL
                    CHECK (category IN ('faq', 'troubleshooting', 'feature',
                                       'billing', 'account', 'general')),
    source          VARCHAR(255) DEFAULT 'product-docs',
    embedding       vector(1536),
    metadata        JSONB DEFAULT '{}',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast approximate nearest neighbor search
CREATE INDEX idx_knowledge_base_embedding ON knowledge_base
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_knowledge_base_category ON knowledge_base(category, is_active);

-- =============================================================================
-- 7. CHANNEL_CONFIGS — Per-channel settings
-- =============================================================================
CREATE TABLE channel_configs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel                 VARCHAR(50) UNIQUE NOT NULL
                            CHECK (channel IN ('email', 'whatsapp', 'web_form')),
    is_enabled              BOOLEAN DEFAULT TRUE,
    max_response_length     INTEGER NOT NULL,
    tone                    VARCHAR(50) NOT NULL
                            CHECK (tone IN ('formal', 'conversational', 'semi-formal')),
    response_template       TEXT,
    api_config_ref          VARCHAR(255),
    metadata                JSONB DEFAULT '{}',
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- 8. AGENT_METRICS — Time-series performance data
-- =============================================================================
CREATE TABLE agent_metrics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type     VARCHAR(100) NOT NULL
                    CHECK (metric_type IN ('response_latency', 'escalation',
                                          'sentiment', 'tool_call',
                                          'conversation_count', 'message_volume')),
    channel         VARCHAR(50)
                    CHECK (channel IS NULL OR
                           channel IN ('email', 'whatsapp', 'web_form')),
    value           FLOAT NOT NULL,
    metadata        JSONB DEFAULT '{}',
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_type_time ON agent_metrics(metric_type, recorded_at);
CREATE INDEX idx_metrics_channel_time ON agent_metrics(channel, recorded_at)
    WHERE channel IS NOT NULL;

-- =============================================================================
-- Updated_at trigger function (reusable)
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at
CREATE TRIGGER trg_customers_updated_at
    BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_conversations_updated_at
    BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_tickets_updated_at
    BEFORE UPDATE ON tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_knowledge_base_updated_at
    BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_channel_configs_updated_at
    BEFORE UPDATE ON channel_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## Seed Data

```sql
-- =============================================================================
-- Seed: Channel Configurations
-- =============================================================================
INSERT INTO channel_configs (channel, is_enabled, max_response_length, tone, response_template, api_config_ref) VALUES
('email', TRUE, 500, 'formal',
 E'Hi {{customer_name}},\n\n{{response_body}}\n\nBest regards,\nTechCorp Support Team\nsupport@techcorp.io | status.techcorp.io',
 'GMAIL_'),
('whatsapp', TRUE, 1600, 'conversational',
 '{{response_body}}',
 'TWILIO_'),
('web_form', TRUE, 300, 'semi-formal',
 E'Hi {{customer_name}},\n\n{{response_body}}\n\nYour ticket reference: {{ticket_number}}\nTrack your ticket at support.techcorp.io',
 NULL);
```

---

## Key Query Patterns

### Identity Resolution (cross-channel matching)
```sql
-- Find customer by any identifier
SELECT c.* FROM customers c
JOIN customer_identifiers ci ON c.id = ci.customer_id
WHERE ci.identifier_type = $1 AND ci.identifier_value = $2;
```

### Knowledge Base Semantic Search
```sql
-- Find top 5 most similar knowledge base entries
SELECT id, title, content, category,
       1 - (embedding <=> $1::vector) AS similarity
FROM knowledge_base
WHERE is_active = TRUE
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

### Customer History (cross-channel)
```sql
-- Get all messages for a customer, ordered chronologically
SELECT m.*, c.channel AS conv_channel
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE m.customer_id = $1
ORDER BY m.created_at DESC
LIMIT $2;
```

### Per-Channel Metrics (last 24h)
```sql
-- Aggregate metrics by channel for the last 24 hours
SELECT
    channel,
    COUNT(*) FILTER (WHERE metric_type = 'conversation_count') AS total_conversations,
    AVG(value) FILTER (WHERE metric_type = 'sentiment') AS avg_sentiment,
    COUNT(*) FILTER (WHERE metric_type = 'escalation') AS escalation_count,
    AVG(value) FILTER (WHERE metric_type = 'response_latency') AS avg_latency_ms
FROM agent_metrics
WHERE recorded_at >= NOW() - INTERVAL '24 hours'
  AND channel IS NOT NULL
GROUP BY channel;
```

---

## Migration Strategy

Migrations are managed as sequential SQL scripts in `production/database/migrations/`:

```
migrations/
├── 001_initial_schema.sql      # Full DDL from above
├── 002_seed_channels.sql       # Channel config seed data
├── 003_seed_knowledge_base.sql # Knowledge base from context/product-docs.md
└── ...
```

Each migration is idempotent where possible (using `IF NOT EXISTS` clauses). The application checks and applies pending migrations on startup.
