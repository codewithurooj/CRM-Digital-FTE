# Quickstart — CRM Digital FTE Local Development

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Web form frontend |
| Docker + Docker Compose | Latest | PostgreSQL, Kafka, Zookeeper |
| minikube | Latest | Kubernetes local cluster (optional, for K8s testing) |
| kubectl | Latest | Kubernetes CLI (optional) |

## 1. Clone and Setup

```bash
git clone <repo-url> CRM-Digital-FTE
cd CRM-Digital-FTE
git checkout 002-customer-success-agent
```

## 2. Environment Variables

Create `production/.env` from the template:

```bash
cp production/.env.example production/.env
```

Required variables:

```env
# Database
DATABASE_URL=postgresql://crm_user:crm_password@localhost:5432/crm_digital_fte

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# OpenAI
OPENAI_API_KEY=sk-...

# Gmail (OAuth2 credentials)
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...
GMAIL_WATCH_EMAIL=support@techcorp.com

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# App Config
LOG_LEVEL=INFO
ENABLED_CHANNELS=web_form,email,whatsapp
API_HOST=0.0.0.0
API_PORT=8000
```

## 3. Start Infrastructure (Docker Compose)

```bash
cd production
docker-compose up -d postgres kafka zookeeper
```

This starts:
- **PostgreSQL 16** with pgvector on port 5432
- **Kafka** on port 9092
- **Zookeeper** on port 2181

## 4. Initialize Database

```bash
# Apply schema
docker exec -i crm-postgres psql -U crm_user -d crm_digital_fte < database/schema.sql

# Seed data (channel configs + knowledge base)
docker exec -i crm-postgres psql -U crm_user -d crm_digital_fte < database/seed.sql
```

## 5. Install Python Dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 6. Run Tests (TDD)

```bash
# All tests with coverage
pytest --cov=production --cov-fail-under=80 -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires Docker services running)
pytest tests/integration/ -v

# Contract tests
pytest tests/contract/ -v
```

## 7. Start the API Server

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs available at: http://localhost:8000/docs

## 8. Start the Worker (Kafka Consumer)

In a separate terminal:

```bash
python -m workers.message_processor
```

## 9. Web Form (React)

```bash
cd ../web-form
npm install
npm run dev
```

Form available at: http://localhost:3000

## 10. Verify Health

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "kafka": "healthy",
    "agent": "healthy"
  },
  "version": "0.1.0",
  "timestamp": "2026-02-08T..."
}
```

## Docker Compose (Full Stack)

To run everything including API and workers:

```bash
docker-compose up -d
```

## Kubernetes (minikube)

```bash
minikube start
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/
minikube service api-service -n crm-digital-fte
```

## Load Testing

```bash
cd tests/load
locust -f locustfile.py --host http://localhost:8000
```

Locust UI: http://localhost:8089
