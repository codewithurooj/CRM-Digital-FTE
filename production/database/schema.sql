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
CREATE TABLE IF NOT EXISTS customers (
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

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone) WHERE phone IS NOT NULL;

-- =============================================================================
-- 2. CUSTOMER_IDENTIFIERS — Cross-channel identity matching
-- =============================================================================
CREATE TABLE IF NOT EXISTS customer_identifiers (
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

CREATE INDEX IF NOT EXISTS idx_identifiers_lookup ON customer_identifiers(identifier_type, identifier_value);
CREATE INDEX IF NOT EXISTS idx_identifiers_customer ON customer_identifiers(customer_id);

-- =============================================================================
-- 3. CONVERSATIONS — Conversation threads with channel tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS conversations (
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

CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id, status);
CREATE INDEX IF NOT EXISTS idx_conversations_channel ON conversations(channel, status);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);

-- =============================================================================
-- 4. MESSAGES — All messages (inbound + outbound) with channel metadata
-- =============================================================================
CREATE TABLE IF NOT EXISTS messages (
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

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_customer ON messages(customer_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel, created_at);

-- =============================================================================
-- 5. TICKETS — Support tickets with status lifecycle
-- =============================================================================
CREATE SEQUENCE IF NOT EXISTS ticket_number_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE IF NOT EXISTS tickets (
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

CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id, status);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status, priority);
CREATE INDEX IF NOT EXISTS idx_tickets_channel ON tickets(source_channel, created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_number ON tickets(ticket_number);

-- Auto-generate TKT-XXXX ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ticket_number := 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ticket_number ON tickets;
CREATE TRIGGER trg_ticket_number
    BEFORE INSERT ON tickets
    FOR EACH ROW
    WHEN (NEW.ticket_number IS NULL OR NEW.ticket_number = '')
    EXECUTE FUNCTION generate_ticket_number();

-- =============================================================================
-- 6. KNOWLEDGE_BASE — Product docs with pgvector embeddings
-- =============================================================================
CREATE TABLE IF NOT EXISTS knowledge_base (
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

CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding ON knowledge_base
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category, is_active);

-- =============================================================================
-- 7. CHANNEL_CONFIGS — Per-channel settings
-- =============================================================================
CREATE TABLE IF NOT EXISTS channel_configs (
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
CREATE TABLE IF NOT EXISTS agent_metrics (
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

CREATE INDEX IF NOT EXISTS idx_metrics_type_time ON agent_metrics(metric_type, recorded_at);
CREATE INDEX IF NOT EXISTS idx_metrics_channel_time ON agent_metrics(channel, recorded_at)
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
DROP TRIGGER IF EXISTS trg_customers_updated_at ON customers;
CREATE TRIGGER trg_customers_updated_at
    BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_conversations_updated_at ON conversations;
CREATE TRIGGER trg_conversations_updated_at
    BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_tickets_updated_at ON tickets;
CREATE TRIGGER trg_tickets_updated_at
    BEFORE UPDATE ON tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_knowledge_base_updated_at ON knowledge_base;
CREATE TRIGGER trg_knowledge_base_updated_at
    BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_channel_configs_updated_at ON channel_configs;
CREATE TRIGGER trg_channel_configs_updated_at
    BEFORE UPDATE ON channel_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at();
