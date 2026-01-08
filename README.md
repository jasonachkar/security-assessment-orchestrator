# Security Assessment Orchestrator (Defensive)

This is a **safe, defensive** alternative to an "auto-exploit pentest framework":
- Orchestrates **Nmap** (discovery/service detection), **ZAP** (web scan), and optional **Trivy** (image scan)
- Persists artifacts to **PostgreSQL**
- Uses **Celery + Redis** for async jobs
- Guardrails: **Bearer token** + **ALLOWED_TARGETS** allowlist

## Run
```bash
cp .env.example .env
docker compose up --build
```

API docs: http://localhost:8082/docs

## Example
```bash
TOKEN="change-me"
curl -s -X POST "http://localhost:8082/assessments"   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"target":"https://localhost"}'
```
