# Dapr Component Generator Agent

## Quick Start

Generate Dapr component configurations with proper credentials and security.

## Usage

### Example 1: Kafka Pub/Sub Component

```bash
"Use dapr-generator agent to create kafka-pubsub component for Redpanda Cloud:
- Bootstrap servers: my-cluster.cloud.redpanda.com:9092
- Authentication: SASL with username/password from kafka-credentials secret
- Consumer group: todo-service
- Used by: backend-service, recurring-task-service, notification-service"
```

**Output:**
- `dapr-components/kafka-pubsub.yaml` - Component definition
- Kubernetes secret manifest
- Deployment annotations for each service
- Integration code (Python + TypeScript)
- Testing commands
- Troubleshooting guide

### Example 2: PostgreSQL State Store

```bash
"Use dapr-generator agent to create statestore component using PostgreSQL:
- Connection string from db-secret Kubernetes secret
- Table name: dapr_state
- Used by: backend-service for conversation state"
```

### Example 3: Dapr Jobs for Reminders

```bash
"Use dapr-generator agent to create dapr-jobs component using PostgreSQL:
- Connection string from db-secret
- Used by: backend-service to schedule reminders
- Integration with /api/jobs/trigger endpoint"
```

### Example 4: Kubernetes Secrets Store

```bash
"Use dapr-generator agent to create kubernetes-secrets component for accessing API keys and credentials"
```

### Example 5: All 5 Components at Once

```bash
"Use dapr-generator agent to create all 5 required Dapr components:
1. kafka-pubsub (Redpanda Cloud with SASL)
2. statestore (PostgreSQL)
3. dapr-jobs (PostgreSQL)
4. kubernetes-secrets
5. Document service invocation pattern

Read credentials from backend/.env for Kafka and database"
```

## What You Get

1. **Component YAML Files**
   - Proper metadata and configuration
   - Secret references (no hardcoded credentials)
   - Scoping to specific apps

2. **Kubernetes Secrets**
   - Secret manifests
   - kubectl commands to create secrets
   - Security best practices

3. **Deployment Updates**
   - Dapr sidecar annotations
   - App-id and port configuration
   - Resource limits for sidecars

4. **Integration Code**
   - Python HTTP API examples
   - TypeScript frontend examples
   - Error handling patterns

5. **Complete Documentation**
   - Component purpose
   - Configuration options
   - Testing procedures
   - Troubleshooting guide

## Integration with Workflow

```bash
# Step 1: Generate Dapr components
"Use dapr-generator agent to create [component]..."

# Step 2: Review component files
ls dapr-components/
cat dapr-components/kafka-pubsub.yaml

# Step 3: Create secrets
kubectl create secret generic kafka-credentials \
  --from-literal=username="..." \
  --from-literal=password="..."

# Step 4: Apply components
kubectl apply -f dapr-components/

# Step 5: Verify
kubectl get components
kubectl describe component kafka-pubsub

# Step 6: Update deployments with annotations
# Add Dapr annotations to Helm charts

# Step 7: Update code to use Dapr APIs
# Replace direct Kafka calls with Dapr HTTP calls
```

## Common Component Types

### Pub/Sub (Kafka, Redis, RabbitMQ)
```bash
"Create kafka-pubsub component for event streaming"
```

### State Store (PostgreSQL, Redis, CosmosDB)
```bash
"Create PostgreSQL state store for conversation state"
```

### Jobs (PostgreSQL, Redis)
```bash
"Create dapr-jobs component for scheduled reminders"
```

### Secrets (Kubernetes, Azure Key Vault, AWS Secrets Manager)
```bash
"Create kubernetes-secrets component for API keys"
```

### Bindings (Twilio, SendGrid, AWS SQS)
```bash
"Create sendgrid binding for email notifications"
```

## Tips

- Provide infrastructure details (Kafka URL, database connection string)
- Specify which services will use the component
- Mention if secrets should come from environment or Kubernetes
- Include any special configuration (timeouts, retries, batching)

## Security Best Practices

The agent automatically:
- Uses Kubernetes secrets for credentials
- Never hardcodes sensitive data
- Scopes components to specific apps
- Provides secret rotation guidance
- Enables mTLS between services (in production)

## Agent Location

`.claude/agents/dapr-generator/agent.md`
