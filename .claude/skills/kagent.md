# kagent Skill

## Description
AI-powered Kubernetes cluster health analysis and recommendations. Continuously monitors clusters, detects issues, and provides actionable recommendations for security, performance, and reliability.

## Installation

```bash
cd scripts
pip install -r requirements.txt
bash install.sh
```

## Configuration

Set up your AI provider (for recommendation generation):

```bash
# Option 1: OpenAI
export OPENAI_API_KEY='your-key-here'

# Option 2: Anthropic Claude
export ANTHROPIC_API_KEY='your-key-here'
```

## Usage Examples

### Full Cluster Analysis

```bash
# Run comprehensive analysis
kagent analyze

# Analyze specific namespace
kagent analyze --namespace production

# Save report
kagent analyze --output markdown --save
kagent analyze --output json --save
```

### Focused Scans

```bash
# Security scan
kagent scan security

# Resource efficiency scan
kagent scan resources --namespace production

# Configuration best practices
kagent scan config

# Performance analysis
kagent scan performance

# Overall health check
kagent scan health
```

### Reports

```bash
# Generate report from latest analysis
kagent report

# Different formats
kagent report --format markdown
kagent report --format json
kagent report --format text

# Save to file
kagent report --format markdown --save
```

### Analysis History

```bash
# View recent analyses
kagent history

# View more entries
kagent history --limit 50
```

### Continuous Monitoring

```bash
# Monitor every hour (default)
kagent monitor

# Custom interval (30 minutes)
kagent monitor --interval 1800

# Monitor specific namespace
kagent monitor --namespace production
```

### Configuration

```bash
# View current configuration
kagent config
```

## When to Use This Skill

Use kagent when you need to:

1. **Cluster Health Analysis**
   - Check overall cluster health
   - Identify unhealthy nodes and pods
   - Monitor system components

2. **Security Auditing**
   - Find privileged containers
   - Detect containers running as root
   - Check for exposed secrets
   - RBAC issues

3. **Resource Optimization**
   - Find missing resource limits
   - Detect over-provisioning
   - Identify inefficient resource usage
   - Storage optimization

4. **Configuration Best Practices**
   - Missing health probes
   - Label inconsistencies
   - Deployment strategies
   - Service configurations

5. **Performance Analysis**
   - Resource bottlenecks
   - Node performance issues
   - Pod density problems

6. **Continuous Monitoring**
   - Scheduled health checks
   - Trend analysis over time
   - Early issue detection

## Analysis Categories

### Health Scanner
- Node status and conditions
- Pod health across namespaces
- System pod health (kube-system)
- Resource pressure indicators
- Cluster size and density

### Resource Analyzer
- Missing requests and limits
- Over-provisioned resources
- Single replica deployments
- High replica counts without HPA
- Ephemeral storage usage

### Configuration Checker
- Missing liveness/readiness probes
- Label best practices
- Update strategies
- Service configurations

### Security Scanner
- Privileged containers
- Containers running as root
- Host network/PID/IPC usage
- Hardcoded secrets in env vars
- Security context configurations
- Read-only filesystems
- Capability drops

### Performance Analyzer
- Under-provisioned resources
- Node performance indicators
- Resource contention
- Pod density issues

## Severity Levels

- **Critical**: Immediate action required (e.g., privileged containers, failed nodes)
- **High**: Important issues (e.g., no resource limits, running as root)
- **Medium**: Best practices (e.g., missing probes, single replicas)
- **Low**: Nice-to-have improvements (e.g., missing labels)

## Report Formats

### Markdown (Default)
- Human-readable
- Formatted tables and lists
- Priority recommendations
- Detailed findings by category

### JSON
- Machine-readable
- Complete data structure
- Easy to parse and integrate
- Trend analysis

### Text
- Plain text output
- Terminal-friendly
- Summary and top issues
- Quick overview

## Common Patterns

### Pattern 1: Daily Health Check

```bash
# Morning health check
kagent analyze --output markdown | less

# Focus on critical issues
kagent scan security
kagent scan health
```

### Pattern 2: Pre-Deployment Check

```bash
# Before deploying to production
kagent analyze --namespace production --save

# Review report
cat ~/.kagent/reports/kagent_report_*.md
```

### Pattern 3: Security Audit

```bash
# Comprehensive security scan
kagent scan security --namespace production

# Generate detailed report
kagent report --format markdown --save
```

### Pattern 4: Resource Optimization

```bash
# Find over/under-provisioned resources
kagent scan resources

# Check for efficiency issues
kagent analyze --namespace production --output json
```

### Pattern 5: Continuous Monitoring

```bash
# Set up continuous monitoring (run in background)
nohup kagent monitor --interval 3600 > /dev/null 2>&1 &

# View trends
kagent history --limit 30
```

## Integration with Claude Code

When generating kagent usage in code or documentation:

```markdown
# Cluster Health Check

## Run Analysis
kagent analyze --namespace production --save

## Review Security Issues
kagent scan security

## Check Resource Efficiency
kagent scan resources

## View Historical Trends
kagent history --limit 14
```

## Recommendations

kagent provides actionable recommendations including:

- **Kubectl commands** to fix issues
- **Configuration changes** to apply
- **Best practice guides** to follow
- **Grouped recommendations** for bulk fixes

Example recommendations:
- "Set runAsNonRoot: true in 15 containers"
- "Add resource limits to 23 deployments"
- "Fix 8 missing liveness probes"

## Limitations

- Requires kubectl to be installed and configured
- AI provider API key required for advanced recommendations
- Some checks require specific Kubernetes permissions
- Performance metrics require metrics-server
- CRDs may not be fully analyzed

## Tips

1. **Run Regularly**: Schedule daily or weekly analyses
   - `kagent monitor --interval 86400`  # Daily

2. **Start with Security**: Critical issues first
   - `kagent scan security`

3. **Save Reports**: Keep history for trend analysis
   - `kagent analyze --save`

4. **Focus on Namespaces**: Analyze production separately
   - `kagent analyze --namespace production`

5. **Review Trends**: Check history for patterns
   - `kagent history --limit 30`

6. **Act on Critical First**: Prioritize by severity
   - Focus on Critical and High severity issues

## Error Handling

kagent provides user-friendly error messages:

- Connection errors → Check kubectl config
- Permission errors → Review RBAC for required permissions
- No findings → Cluster is healthy!
- AI API errors → Recommendations will use rule-based fallback

## Support

For issues or questions:
- Check configuration: `kagent config`
- View audit log: `kagent audit`
- Enable debug mode: `kagent --debug analyze`
- Review analysis history: `kagent history`

## Example Workflow

```bash
# 1. Initial cluster scan
kagent analyze --save

# 2. Review critical issues
grep -i "critical" ~/.kagent/reports/kagent_report_*.md

# 3. Fix security issues first
kagent scan security

# 4. Apply recommendations
kubectl edit deployment <name> -n <namespace>
# Add recommended fixes

# 5. Re-scan to verify
kagent analyze --namespace <namespace>

# 6. Set up monitoring
kagent monitor --interval 3600
```

## Best Practices

1. **Baseline First**: Run initial analysis to establish baseline
2. **Fix Critical**: Address critical and high severity issues immediately
3. **Track Progress**: Save reports and compare over time
4. **Automate**: Use continuous monitoring for early detection
5. **Document**: Keep reports for compliance and audits
6. **Integrate**: Include in CI/CD pipelines for pre-deployment checks
