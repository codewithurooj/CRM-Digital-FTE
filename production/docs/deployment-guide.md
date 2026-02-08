# Deployment Guide — CRM Digital FTE

## Prerequisites

- Docker & Docker Compose
- kubectl + minikube (for K8s deployment)
- Python 3.11+
- Node.js 18+ (for web form)

## Local Development (Docker Compose)

### 1. Setup Environment

```bash
cd production
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN (optional)
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN (optional)
```

### 2. Start Infrastructure

```bash
docker-compose up -d
```

This starts:
- PostgreSQL 16 + pgvector (port 5432)
- Kafka + Zookeeper (port 9092)

### 3. Initialize Database

```bash
# Apply schema
docker exec -i crm-postgres psql -U crm -d crm_digital_fte < database/schema.sql

# Load seed data
docker exec -i crm-postgres psql -U crm -d crm_digital_fte < database/seed.sql
```

### 4. Run API Server

```bash
pip install -r requirements.txt
uvicorn production.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run Worker

```bash
python -m production.workers.message_processor
```

### 6. Build Web Form

```bash
cd ../web-form
npm install
npm run dev
```

### 7. Run Tests

```bash
cd ../production
pip install -r requirements-dev.txt
pytest tests/ -v --cov=production --cov-fail-under=80
```

## Kubernetes Deployment

### 1. Build Docker Image

```bash
cd production
docker build -t crm-digital-fte:latest .
```

### 2. Start minikube

```bash
minikube start --memory=4096 --cpus=4
eval $(minikube docker-env)
docker build -t crm-digital-fte:latest .
```

### 3. Apply K8s Manifests

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (edit with real values first!)
kubectl apply -f k8s/secrets.yaml

# Create config
kubectl apply -f k8s/configmap.yaml

# Deploy infrastructure
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/kafka-deployment.yaml

# Wait for infrastructure
kubectl -n crm-digital-fte wait --for=condition=ready pod -l app=postgres --timeout=120s
kubectl -n crm-digital-fte wait --for=condition=ready pod -l app=kafka --timeout=120s

# Deploy application
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml

# Configure auto-scaling
kubectl apply -f k8s/api-hpa.yaml
kubectl apply -f k8s/worker-hpa.yaml
```

### 4. Verify Deployment

```bash
kubectl -n crm-digital-fte get pods
kubectl -n crm-digital-fte get services

# Check health
kubectl -n crm-digital-fte port-forward svc/api-service 8000:80
curl http://localhost:8000/api/v1/health
```

### 5. Access the API

```bash
# Port forward
kubectl -n crm-digital-fte port-forward svc/api-service 8000:80

# Or use minikube service
minikube -n crm-digital-fte service api-service --url
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | System health check |
| POST | /api/v1/support/form | Submit web support form |
| GET | /api/v1/tickets/{id} | Get ticket status |
| GET | /api/v1/metrics/channels | Per-channel metrics |
| POST | /api/v1/webhooks/gmail | Gmail Pub/Sub webhook |
| POST | /api/v1/webhooks/whatsapp | Twilio WhatsApp webhook |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| KAFKA_BOOTSTRAP_SERVERS | Yes | - | Kafka broker address |
| OPENAI_API_KEY | Yes | - | OpenAI API key for GPT-4o |
| GMAIL_CLIENT_ID | No | "" | Gmail OAuth client ID |
| GMAIL_CLIENT_SECRET | No | "" | Gmail OAuth client secret |
| GMAIL_REFRESH_TOKEN | No | "" | Gmail OAuth refresh token |
| TWILIO_ACCOUNT_SID | No | "" | Twilio account SID |
| TWILIO_AUTH_TOKEN | No | "" | Twilio auth token |
| LOG_LEVEL | No | INFO | Logging level |
| API_PORT | No | 8000 | API server port |

## Monitoring

- Health: `GET /api/v1/health`
- Metrics: `GET /api/v1/metrics/channels?period_hours=24`
- Logs: `kubectl -n crm-digital-fte logs -f deployment/api`
- Worker: `kubectl -n crm-digital-fte logs -f deployment/worker`
