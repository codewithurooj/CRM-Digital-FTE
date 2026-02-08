# kubectl-ai Skill

## Description
Natural language interface for Kubernetes operations. Translates natural language commands into kubectl operations with AI assistance and user confirmation for destructive actions.

## Installation

```bash
cd scripts
pip install -r requirements.txt
bash install.sh
```

## Configuration

Set up your AI provider:

```bash
# Option 1: OpenAI
export OPENAI_API_KEY='your-key-here'

# Option 2: Anthropic Claude
export ANTHROPIC_API_KEY='your-key-here'
```

## Usage Examples

### Basic Commands

```bash
# List resources
kubectl-ai execute "list all pods"
kubectl-ai execute "show deployments in production namespace"
kubectl-ai execute "get all services"

# Describe resources
kubectl-ai execute "describe pod nginx-pod"
kubectl-ai execute "show details of deployment api-server"

# Get logs
kubectl-ai execute "show logs for pod app-123"
kubectl-ai execute "tail logs from failing-pod"
```

### Scaling Operations

```bash
# Scale deployments
kubectl-ai execute "scale nginx deployment to 5 replicas"
kubectl-ai execute "scale down api-server to 2 replicas"
```

### Destructive Operations (Requires Confirmation)

```bash
# Delete resources (will prompt for confirmation)
kubectl-ai execute "delete pod stuck-pod"
kubectl-ai execute "remove deployment old-app"

# Skip confirmation (use with caution)
kubectl-ai execute "delete pod test-pod" --no-confirm
```

### Troubleshooting

```bash
# Analyze problems
kubectl-ai troubleshoot "pod keeps restarting"
kubectl-ai troubleshoot "service not accessible"
kubectl-ai troubleshoot "deployment stuck in pending"
```

### Dry Run Mode

```bash
# See what would be executed without running
kubectl-ai execute "delete all pods in test namespace" --dry-run
```

### Configuration and Audit

```bash
# View current configuration
kubectl-ai config

# View audit log
kubectl-ai audit --limit 50

# View usage statistics
kubectl-ai stats --days 7
```

## When to Use This Skill

Use kubectl-ai when you need to:

1. **Natural Language Kubernetes Operations**
   - Convert plain English to kubectl commands
   - Example: "scale nginx to 5 replicas" → `kubectl scale deployment nginx --replicas=5`

2. **Safe Destructive Operations**
   - Delete, remove, or destroy resources with automatic confirmation
   - Audit trail of all operations

3. **Troubleshooting Kubernetes Issues**
   - AI-powered analysis of problems
   - Suggested diagnostic commands
   - Step-by-step solutions

4. **Learning Kubernetes**
   - See kubectl commands generated from natural language
   - Understand what commands do before running them

## Safety Features

- **Confirmation Required**: Destructive operations require user confirmation
- **Audit Logging**: All operations logged with timestamps
- **Command Validation**: Prevents command injection and dangerous patterns
- **Dry Run Mode**: Preview commands without execution

## Common Patterns

### Pattern 1: Quick Resource Check

```bash
kubectl-ai execute "list all pods in production"
```

### Pattern 2: Scale Application

```bash
kubectl-ai execute "scale my-app deployment to 10 replicas in production namespace"
```

### Pattern 3: Debug Pod Issues

```bash
kubectl-ai troubleshoot "pod my-app-abc123 keeps crashing"
```

### Pattern 4: Clean Up Resources

```bash
kubectl-ai execute "delete all completed jobs" --dry-run  # Check first
kubectl-ai execute "delete all completed jobs"  # Then execute
```

## Integration with Claude Code

When generating kubectl-ai usage in code or documentation:

```markdown
# Use kubectl-ai for Kubernetes operations

## Scale deployment
kubectl-ai execute "scale api-deployment to 3 replicas"

## Check pod health
kubectl-ai troubleshoot "api pods not responding"

## View logs
kubectl-ai execute "show logs for api-deployment pods"
```

## Limitations

- Requires kubectl to be installed and configured
- AI provider API key required (OpenAI or Anthropic)
- Complex multi-step operations may need manual kubectl commands
- CRDs and custom resources may not be fully supported yet

## Tips

1. **Be Specific**: More details lead to better command generation
   - ✅ "scale nginx deployment in production to 5 replicas"
   - ❌ "scale nginx"

2. **Use Dry Run First**: For destructive operations, use --dry-run
   - `kubectl-ai execute "delete old pods" --dry-run`

3. **Check Audit Log**: Review what operations have been performed
   - `kubectl-ai audit --limit 100`

4. **Troubleshoot with Context**: Provide details about the problem
   - ✅ "deployment stuck with ImagePullBackOff error"
   - ❌ "deployment not working"

## Error Handling

kubectl-ai provides user-friendly error messages:

- Connection errors → Check kubectl config and cluster access
- Permission errors → Review RBAC settings
- AI API errors → Check API key and quota
- Resource not found → Verify resource name and namespace

## Support

For issues or questions:
- Check audit log: `kubectl-ai audit`
- Enable debug mode: `kubectl-ai --debug execute "your command"`
- View configuration: `kubectl-ai config`
