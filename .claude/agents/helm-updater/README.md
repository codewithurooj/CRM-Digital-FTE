# Helm Chart Updater Agent

## Quick Start

Update Helm charts as application features evolve without breaking deployments.

## Usage

### Example 1: Add Kafka Environment Variables

```bash
"Use helm-updater agent to add Kafka configuration to backend Helm chart:
- KAFKA_BOOTSTRAP_SERVERS (default: kafka:9092)
- KAFKA_TOPIC (default: task-events)
- KAFKA_CONSUMER_GROUP (default: backend-group)
Also create values-cloud.yaml with Redpanda Cloud bootstrap servers"
```

**Output:**
- Updated `charts/backend/Chart.yaml` (version bump)
- Updated `charts/backend/values.yaml` (new env vars)
- New `charts/backend/values-cloud.yaml` (cloud config)
- Migration guide
- Testing commands
- Deployment instructions

### Example 2: Add Dapr Sidecar Annotations

```bash
"Use helm-updater agent to add Dapr sidecar to backend chart:
- Enable Dapr sidecar
- App ID: backend-service
- App port: 8000
- Log level: info
Update deployment.yaml template with annotations"
```

### Example 3: Increase Resources for Kafka Processing

```bash
"Use helm-updater agent to increase backend resources:
- CPU limit: 500m → 1000m
- Memory limit: 512Mi → 1Gi
- Reason: Kafka message processing workload increased"
```

### Example 4: Add ConfigMap for Application Config

```bash
"Use helm-updater agent to add ConfigMap to frontend chart:
- Create configmap.yaml template
- Add feature flags
- Mount as volume in deployment
Update values.yaml with config.enabled and config.data sections"
```

### Example 5: Add Secret References

```bash
"Use helm-updater agent to add database secret reference to backend chart:
- Secret name: db-secret
- Key: DATABASE_URL
- Update deployment.yaml to use secretKeyRef
- Document secret creation in README"
```

## What You Get

1. **Updated Chart Files**
   - Chart.yaml with version bump
   - values.yaml with new defaults
   - deployment.yaml updates (if needed)
   - New templates (configmap, secret refs)

2. **Multi-Environment Support**
   - values-cloud.yaml for production
   - values-dev.yaml for development
   - Environment-specific overrides

3. **Validation**
   - `helm lint` commands
   - Template rendering tests
   - Dry-run installation
   - Rollback procedure

4. **Documentation**
   - Updated README with new config
   - Migration guide for upgrades
   - Required secrets documentation
   - Example deployment commands

5. **Changelog**
   - Version change rationale
   - Breaking changes (if any)
   - Backward compatibility notes

## Integration with Workflow

```bash
# Step 1: Request Helm update
"Use helm-updater agent to add [configuration]..."

# Step 2: Review changes
git diff charts/backend/

# Step 3: Validate chart
helm lint charts/backend
helm template test charts/backend --debug

# Step 4: Test upgrade on dev
helm upgrade backend charts/backend --dry-run --debug

# Step 5: Apply to dev environment
helm upgrade backend charts/backend

# Step 6: Verify
kubectl get pods
kubectl describe deployment backend
helm status backend

# Step 7: Deploy to production (with cloud values)
helm upgrade backend charts/backend \
  -f charts/backend/values-cloud.yaml \
  --set image.tag=v1.2.3

# Step 8: Rollback if needed
helm rollback backend
```

## Common Update Types

### Environment Variables
```bash
"Add env var LOG_LEVEL=info to backend chart"
```

### Resource Limits
```bash
"Increase backend memory limit to 2Gi"
```

### Dapr Integration
```bash
"Enable Dapr sidecar for backend service"
```

### Secrets
```bash
"Add secret reference for OPENAI_API_KEY from api-keys secret"
```

### ConfigMaps
```bash
"Create ConfigMap for app-config.json with feature flags"
```

### Ingress
```bash
"Add ingress configuration for todo.example.com with TLS"
```

### Probes
```bash
"Add liveness probe at /health and readiness probe at /ready"
```

## Tips

- Always specify which chart (frontend/backend/service-name)
- Mention if change affects cloud or local deployments
- Include default values for new configuration
- Note if secrets need to be created
- Specify if backward compatibility is required

## Versioning Guide

Agent follows semantic versioning:

- **PATCH (1.0.X):** Bug fix, no API changes
  - Example: "Fix ConfigMap indentation"

- **MINOR (1.X.0):** New feature, backward compatible
  - Example: "Add Kafka env vars with defaults"

- **MAJOR (X.0.0):** Breaking change
  - Example: "Change image repository location"

## Before and After Example

### Before
```yaml
# values.yaml
env:
  NODE_ENV: "production"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
```

### After
```yaml
# values.yaml
env:
  NODE_ENV: "production"
  KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"  # Added

resources:
  limits:
    cpu: 1000m    # Increased
    memory: 1Gi   # Increased

dapr:              # Added
  enabled: true
  appId: "backend-service"
```

## Agent Location

`.claude/agents/helm-updater/agent.md`
