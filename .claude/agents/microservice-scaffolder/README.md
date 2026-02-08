# Microservice Scaffolder Agent

## Quick Start

Generate complete, production-ready microservice from a specification.

## Usage

### Example 1: Recurring Task Service

```bash
"Use microservice-scaffolder agent to create Recurring Task Service that:
- Consumes task-events Kafka topic
- Listens for event_type='completed'
- When recurring task completed, calculates next due_date
- Creates new task with same title, description, priority, tags
- Includes Dockerfile and Helm chart"
```

**Output:**
```
services/recurring-task-service/
├── app/
│   ├── main.py           # Service entry point
│   ├── consumer.py       # Kafka consumer
│   ├── config.py         # Configuration
│   └── models.py         # Data models
├── tests/                # Unit tests
├── Dockerfile            # Production container
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```

Plus:
```
charts/recurring-task-service/
├── Chart.yaml
├── values.yaml
└── templates/
    └── deployment.yaml
```

### Example 2: Notification Service

```bash
"Use microservice-scaffolder agent to create Notification Service that:
- Consumes reminders Kafka topic
- Schedules notifications using Dapr Jobs API
- Sends browser notifications at scheduled time
- Includes health checks and graceful shutdown"
```

### Example 3: Audit Log Service

```bash
"Use microservice-scaffolder agent to create Audit Service that:
- Consumes task-events topic (all events)
- Logs every operation to audit_log table
- Includes timestamp, user_id, action, and data
- Deployed with 1 replica"
```

## What You Get

1. **Complete Service Code**
   - Kafka consumer with error handling
   - Graceful shutdown on SIGTERM
   - Structured logging
   - Configuration management

2. **Production Dockerfile**
   - Multi-stage build
   - Non-root user
   - Optimized layers
   - Health checks

3. **Helm Chart**
   - Deployment with resource limits
   - Dapr sidecar annotations
   - ConfigMap for configuration
   - Secret references

4. **Tests**
   - Unit tests for business logic
   - Mock fixtures
   - Test configuration

5. **Complete Documentation**
   - Service purpose
   - Local development setup
   - Deployment instructions
   - Troubleshooting guide

## Integration with Workflow

```bash
# Step 1: Generate microservice
"Use microservice-scaffolder agent to create [Service Name]..."

# Step 2: Review generated code
cd services/[service-name]
cat README.md

# Step 3: Test locally
pip install -r requirements.txt
python -m app.main

# Step 4: Build and deploy
docker build -t [service-name]:latest .
helm install [service-name] ./charts/[service-name]

# Step 5: Verify
kubectl get pods -l app=[service-name]
kubectl logs -f deployment/[service-name]
```

## Tips

- Provide clear service purpose and event schema
- Specify Kafka topic and consumer group
- Mention any database interactions needed
- Indicate if Dapr integration required
- Include resource requirements if known

## Example Prompts

**Simple:**
```
"Create microservice for processing reminders"
```

**Detailed:**
```
"Use microservice-scaffolder agent to create Notification Service:
- Consumer group: notification-service-group
- Topic: reminders
- On event: schedule via Dapr Jobs API at remind_at time
- On trigger: send browser notification to user
- Database: PostgreSQL to mark reminded=true
- Resources: 250m CPU, 256Mi memory
- Replicas: 1
- Dapr enabled: yes"
```

## Agent Location

`.claude/agents/microservice-scaffolder/agent.md`
