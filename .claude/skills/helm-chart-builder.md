# Helm Chart Builder Skill

## Purpose
Automatically generate production-ready Helm charts for Kubernetes deployments. Creates complete chart structure with deployment, service, ingress, configmap, and secret templates following Kubernetes and Helm best practices.

## Capabilities
- Generate complete Helm chart directory structure
- Create parameterized deployment manifests
- Generate service configurations (ClusterIP, NodePort, LoadBalancer)
- Create ingress rules with TLS support
- Add ConfigMaps and Secrets management
- Include helpful templates (_helpers.tpl)
- Generate values.yaml with sensible defaults
- Support multiple environments (dev, staging, prod)
- Include resource limits and requests
- Add health checks (liveness, readiness, startup probes)

## Input Parameters
```typescript
{
  chartName: string;          // Chart name (e.g., "frontend", "backend")
  appType: 'frontend' | 'backend' | 'service';
  image: string;              // Docker image name
  port: number;               // Container port
  replicas: number;           // Number of replicas
  ingressEnabled: boolean;    // Enable ingress
  ingressHost?: string;       // Ingress hostname
  envVars?: EnvVar[];         // Environment variables
  secrets?: Secret[];         // Secret values
  resources?: Resources;      // Resource limits/requests
}

interface EnvVar {
  name: string;
  value: string;
  fromConfigMap?: boolean;
  fromSecret?: boolean;
}

interface Secret {
  name: string;
  value: string;
}

interface Resources {
  limits: { cpu: string; memory: string; }
  requests: { cpu: string; memory: string; }
}
```

## Output Structure

### Generated Chart Structure
```
charts/{chartName}/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── values-dev.yaml         # Development overrides
├── values-prod.yaml        # Production overrides
├── .helmignore            # Exclude files from packaging
├── templates/
│   ├── _helpers.tpl       # Template helpers
│   ├── deployment.yaml    # Deployment manifest
│   ├── service.yaml       # Service manifest
│   ├── ingress.yaml       # Ingress rules (optional)
│   ├── configmap.yaml     # ConfigMap (if envVars)
│   ├── secret.yaml        # Secrets (if secrets)
│   ├── hpa.yaml           # Horizontal Pod Autoscaler (optional)
│   └── NOTES.txt          # Post-install notes
└── README.md              # Chart documentation
```

## Helm Chart Templates

### 1. Chart.yaml

**File:** `charts/{chartName}/Chart.yaml`

```yaml
apiVersion: v2
name: {{ chartName }}
description: A Helm chart for {{ chartName }} deployment
type: application
version: 1.0.0
appVersion: "1.0"
keywords:
  - {{ chartName }}
  - kubernetes
  - helm
home: https://github.com/yourusername/{{ chartName }}
maintainers:
  - name: Your Name
    email: your.email@example.com
```

---

### 2. values.yaml (Default)

**File:** `charts/{chartName}/values.yaml`

```yaml
# Default values for {{ chartName }}
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

replicaCount: 2

image:
  repository: {{ image }}
  pullPolicy: IfNotPresent
  # Overrides the image tag whose default is the chart appVersion.
  tag: "latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  # Specifies whether a service account should be created
  create: true
  # Annotations to add to the service account
  annotations: {}
  # The name of the service account to use.
  name: ""

podAnnotations: {}

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: false

service:
  type: ClusterIP
  port: {{ port }}
  targetPort: {{ port }}
  annotations: {}

ingress:
  enabled: {{ ingressEnabled }}
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: {{ ingressHost || 'app.local' }}
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: {{ chartName }}-tls
      hosts:
        - {{ ingressHost || 'app.local' }}

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}

# Environment variables
env: []
  # - name: NODE_ENV
  #   value: production
  # - name: API_URL
  #   value: http://backend:8000

# Environment variables from ConfigMap
envFrom: []
  # - configMapRef:
  #     name: {{ chartName }}-config

# Health checks
livenessProbe:
  httpGet:
    path: /health
    port: {{ port }}
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: {{ port }}
  initialDelaySeconds: 20
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /health
    port: {{ port }}
  initialDelaySeconds: 0
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 30
```

---

### 3. values-dev.yaml (Development)

**File:** `charts/{chartName}/values-dev.yaml`

```yaml
# Development environment overrides

replicaCount: 1

image:
  pullPolicy: Never  # Use local images in Minikube
  tag: "latest"

resources:
  limits:
    cpu: 250m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

ingress:
  enabled: true
  hosts:
    - host: {{ chartName }}.local
      paths:
        - path: /
          pathType: Prefix
  tls: []  # No TLS in dev

env:
  - name: NODE_ENV
    value: development
  - name: LOG_LEVEL
    value: debug

autoscaling:
  enabled: false
```

---

### 4. values-prod.yaml (Production)

**File:** `charts/{chartName}/values-prod.yaml`

```yaml
# Production environment overrides

replicaCount: 3

image:
  pullPolicy: Always
  tag: "v1.0.0"  # Use specific version

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

ingress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: {{ ingressHost }}
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: {{ chartName }}-tls
      hosts:
        - {{ ingressHost }}

env:
  - name: NODE_ENV
    value: production
  - name: LOG_LEVEL
    value: info

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

---

### 5. templates/_helpers.tpl

**File:** `charts/{chartName}/templates/_helpers.tpl`

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "{{ chartName }}.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "{{ chartName }}.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "{{ chartName }}.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "{{ chartName }}.labels" -}}
helm.sh/chart: {{ include "{{ chartName }}.chart" . }}
{{ include "{{ chartName }}.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "{{ chartName }}.selectorLabels" -}}
app.kubernetes.io/name: {{ include "{{ chartName }}.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "{{ chartName }}.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "{{ chartName }}.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

---

### 6. templates/deployment.yaml

**File:** `charts/{chartName}/templates/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "{{ chartName }}.fullname" . }}
  labels:
    {{- include "{{ chartName }}.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "{{ chartName }}.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "{{ chartName }}.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "{{ chartName }}.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: {{ .Chart.Name }}
        securityContext:
          {{- toYaml .Values.securityContext | nindent 12 }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.targetPort }}
          protocol: TCP
        {{- if .Values.livenessProbe }}
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 12 }}
        {{- end }}
        {{- if .Values.readinessProbe }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 12 }}
        {{- end }}
        {{- if .Values.startupProbe }}
        startupProbe:
          {{- toYaml .Values.startupProbe | nindent 12 }}
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
        {{- with .Values.env }}
        env:
          {{- toYaml . | nindent 12 }}
        {{- end }}
        {{- with .Values.envFrom }}
        envFrom:
          {{- toYaml . | nindent 12 }}
        {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

---

### 7. templates/service.yaml

**File:** `charts/{chartName}/templates/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "{{ chartName }}.fullname" . }}
  labels:
    {{- include "{{ chartName }}.labels" . | nindent 4 }}
  {{- with .Values.service.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "{{ chartName }}.selectorLabels" . | nindent 4 }}
```

---

### 8. templates/ingress.yaml

**File:** `charts/{chartName}/templates/ingress.yaml`

```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "{{ chartName }}.fullname" . }}
  labels:
    {{- include "{{ chartName }}.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "{{ chartName }}.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

---

### 9. templates/configmap.yaml

**File:** `charts/{chartName}/templates/configmap.yaml`

```yaml
{{- if .Values.env }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "{{ chartName }}.fullname" . }}-config
  labels:
    {{- include "{{ chartName }}.labels" . | nindent 4 }}
data:
  {{- range .Values.env }}
  {{- if not .fromSecret }}
  {{ .name }}: {{ .value | quote }}
  {{- end }}
  {{- end }}
{{- end }}
```

---

### 10. templates/secret.yaml

**File:** `charts/{chartName}/templates/secret.yaml`

```yaml
{{- if .Values.secrets }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "{{ chartName }}.fullname" . }}-secret
  labels:
    {{- include "{{ chartName }}.labels" . | nindent 4 }}
type: Opaque
data:
  {{- range .Values.secrets }}
  {{ .name }}: {{ .value | b64enc | quote }}
  {{- end }}
{{- end }}
```

---

### 11. templates/hpa.yaml (Horizontal Pod Autoscaler)

**File:** `charts/{chartName}}/templates/hpa.yaml`

```yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "{{ chartName }}.fullname" . }}
  labels:
    {{- include "{{ chartName }}.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "{{ chartName }}.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    {{- if .Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
{{- end }}
```

---

### 12. templates/NOTES.txt

**File:** `charts/{chartName}/templates/NOTES.txt`

```
1. Get the application URL by running these commands:
{{- if .Values.ingress.enabled }}
{{- range $host := .Values.ingress.hosts }}
  {{- range .paths }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ $host.host }}{{ .path }}
  {{- end }}
{{- end }}
{{- else if contains "NodePort" .Values.service.type }}
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "{{ chartName }}.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
{{- else if contains "LoadBalancer" .Values.service.type }}
     NOTE: It may take a few minutes for the LoadBalancer IP to be available.
           You can watch the status of by running 'kubectl get --namespace {{ .Release.Namespace }} svc -w {{ include "{{ chartName }}.fullname" . }}'
  export SERVICE_IP=$(kubectl get svc --namespace {{ .Release.Namespace }} {{ include "{{ chartName }}.fullname" . }} --template "{{"{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}"}}")
  echo http://$SERVICE_IP:{{ .Values.service.port }}
{{- else if contains "ClusterIP" .Values.service.type }}
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "{{ chartName }}.name" . }},app.kubernetes.io/instance={{ .Release.Name }}" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace {{ .Release.Namespace }} $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace {{ .Release.Namespace }} port-forward $POD_NAME 8080:$CONTAINER_PORT
{{- end }}
```

---

### 13. .helmignore

**File:** `charts/{chartName}/.helmignore`

```
# Patterns to ignore when building packages.
*.swp
*.bak
*.tmp
*.orig
*~
.DS_Store
.git/
.gitignore
.bzr/
.bzrignore
.hg/
.hgignore
.svn/
*.tgz
.idea/
.vscode/
*.log
README.md
```

---

### 14. README.md

**File:** `charts/{chartName}/README.md`

```markdown
# {{ chartName }} Helm Chart

## Installation

### Install with default values
\`\`\`bash
helm install {{ chartName }} ./charts/{{ chartName }}
\`\`\`

### Install with development values
\`\`\`bash
helm install {{ chartName }} ./charts/{{ chartName }} -f charts/{{ chartName }}/values-dev.yaml
\`\`\`

### Install with production values
\`\`\`bash
helm install {{ chartName }} ./charts/{{ chartName }} -f charts/{{ chartName }}/values-prod.yaml
\`\`\`

## Upgrading

\`\`\`bash
helm upgrade {{ chartName }} ./charts/{{ chartName }}
\`\`\`

## Uninstalling

\`\`\`bash
helm uninstall {{ chartName }}
\`\`\`

## Configuration

See \`values.yaml\` for all configurable parameters.

### Common Overrides

\`\`\`bash
# Set replica count
helm install {{ chartName }} ./charts/{{ chartName }} --set replicaCount=3

# Set image tag
helm install {{ chartName }} ./charts/{{ chartName }} --set image.tag=v1.2.3

# Enable ingress
helm install {{ chartName }} ./charts/{{ chartName }} --set ingress.enabled=true

# Set resource limits
helm install {{ chartName }} ./charts/{{ chartName }} \\
  --set resources.limits.cpu=1000m \\
  --set resources.limits.memory=1Gi
\`\`\`

## Verification

\`\`\`bash
# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/{{ chartName }}

# Check health
kubectl get pods -w
\`\`\`
```

---

## Usage Examples

### Example 1: Generate Frontend Chart

```bash
# User command
"Use helm-chart-builder to create Helm chart for todo-frontend"

# Parameters:
- chartName: frontend
- appType: frontend
- image: todo-frontend
- port: 3000
- replicas: 2
- ingressEnabled: true
- ingressHost: todo.local

# Claude generates:
✅ charts/frontend/ (complete structure)
✅ All templates with proper labels
✅ values.yaml with Next.js optimizations
✅ values-dev.yaml for Minikube
✅ values-prod.yaml for cloud

# Ready to deploy:
helm install frontend ./charts/frontend
```

### Example 2: Generate Backend Chart

```bash
# User command
"Create Helm chart for backend with ConfigMap and Secrets"

# Claude generates:
✅ charts/backend/ (complete structure)
✅ ConfigMap for DATABASE_URL
✅ Secret for OPENAI_API_KEY
✅ Health checks on /health
✅ Resource limits configured

# Deploy:
helm install backend ./charts/backend -f charts/backend/values-dev.yaml
```

---

## Helm Commands Reference

### Installation
```bash
# Install chart
helm install <release-name> <chart-path>

# Install with custom values
helm install <release-name> <chart-path> -f custom-values.yaml

# Install with overrides
helm install <release-name> <chart-path> --set key=value

# Dry run (test)
helm install <release-name> <chart-path> --dry-run --debug
```

### Management
```bash
# List releases
helm list

# Upgrade release
helm upgrade <release-name> <chart-path>

# Rollback
helm rollback <release-name> <revision>

# Uninstall
helm uninstall <release-name>

# Get status
helm status <release-name>
```

### Debugging
```bash
# Render templates
helm template <chart-path>

# Validate chart
helm lint <chart-path>

# Show values
helm get values <release-name>

# Show manifest
helm get manifest <release-name>
```

---

## Time Savings

**Manual Helm Chart Creation:**
- Research Helm structure: 1 hour
- Write templates: 2-3 hours
- Configure values: 1 hour
- Test and debug: 1-2 hours
- **Total: 5-7 hours per chart**

**With This Skill:**
- Generation: 2 minutes
- Review/customize: 15 minutes
- **Total: 20 minutes per chart**

**Time Saved: 95%** ⚡

---

## Quality Benefits

✅ **Production-Ready** - Best practices built-in
✅ **Secure** - Pod security contexts, non-root users
✅ **Scalable** - HPA support, resource limits
✅ **Observable** - Health checks, proper labels
✅ **Flexible** - Multiple environment support

---

## Reusability

Use this skill for:
- **Phase 4:** Minikube deployment
- **Phase 5:** Cloud deployment, microservices
- **Future Projects:** Any Kubernetes deployment

---

**This skill generates production-ready Helm charts in minutes!** ⎈
