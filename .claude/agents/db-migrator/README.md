# Database Migration Agent

## Quick Start

Generate complete database migration plan from a feature specification.

## Usage

### Example 1: Add Priority and Tags to Tasks

```bash
"Use db-migrator agent to generate migration for adding priority (high/medium/low) and tags (text array) columns to tasks table from @specs/features/intermediate-features.md"
```

**Output:**
- Migration SQL scripts (forward + rollback)
- Updated SQLModel definitions
- Validation queries
- Testing checklist
- Risk assessment
- Deployment procedure

### Example 2: Add Recurring Task Fields

```bash
"Use db-migrator agent to create migration for recurring tasks feature: add recurring VARCHAR(20), recurring_interval INTEGER, parent_task_id INTEGER (foreign key to tasks.id)"
```

### Example 3: Add Due Dates and Reminders

```bash
"Use db-migrator agent to add due_date TIMESTAMP, remind_at TIMESTAMP, and reminded BOOLEAN columns to tasks table"
```

## What You Get

1. **Forward Migration SQL**
   - Safe ALTER TABLE statements
   - CREATE INDEX CONCURRENTLY for zero downtime
   - Proper constraints and defaults

2. **Rollback Migration SQL**
   - Undo changes if needed
   - Safe to run in production

3. **Updated SQLModel**
   - Python models matching new schema
   - Field validators and types
   - Index definitions

4. **Validation Queries**
   - Verify migration success
   - Check data integrity

5. **Documentation**
   - Risk assessment
   - Testing checklist
   - Deployment steps

## Integration with Workflow

```bash
# Step 1: Generate migration
"Use db-migrator agent from @specs/features/my-feature.md"

# Step 2: Review output
# Check migration files in specs/features/my-feature/migration.md

# Step 3: Test on dev database
psql $DATABASE_URL -f migrations/001_my_feature.sql

# Step 4: Update SQLModel
# Copy model updates to backend/app/models.py

# Step 5: Apply to production
# Follow deployment procedure in migration.md
```

## Tips

- Always provide the feature spec file path with `@specs/...`
- Agent analyzes existing schema from `specs/database/schema.md`
- Reviews current models from `backend/app/models.py`
- Generates zero-downtime migrations when possible

## Agent Location

`.claude/agents/db-migrator/agent.md`
