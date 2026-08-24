# SentinelAI Technology Stack

## Version

v2.0 — reconciled with actual implementation (previous version described the originally planned stack, most of which was never built; see "Planned / Future" section below for what's still aspirational).

---

# Current Implementation

Updated after the security/architecture pass and subsequent feature work
(RBAC, audit logging, alert lifecycle, Alembic migrations, tests/CI, asset
management, IOC/threat intel, AI analysis). The "Sprint 5" baseline this
document originally described has moved on substantially - see git history
for the specifics.

## Frontend

* **Vite** + **React 19** (JSX, no TypeScript)
* Hand-written CSS (no Tailwind, no Shadcn UI)
* Plain `fetch()` calls to the backend, no API client library, no state management library, no router (single-page dashboard in `App.jsx`)

## Backend

* **FastAPI**
* **Python 3.13**
* **SQLAlchemy** ORM
* **Alembic** manages the schema (`backend/alembic/`) — `create_all` was removed from `main.py`; run `alembic upgrade head` after setup
* **python-jose** for JWT encode/decode, **passlib[bcrypt]** for password hashing

## Database

* **PostgreSQL**, connected via `DATABASE_URL` in `backend/.env` (no Redis, no caching layer)

## Security

* JWT bearer auth (`core/security.py`, `core/dependencies.py`)
* bcrypt password hashing
* Role-based access control enforced server-side (`core/dependencies.require_role`) — admin/security_manager/analyst/viewer
* Audit logging (`services/audit_service.py`, `audit_logs` table) on every security-sensitive action

## Detection & Correlation

* Rule-based: brute-force threshold (`services/risk_engine.py`) and IOC/IP indicator matching (`services/ioc_matcher.py`) against a real `iocs` table, wired into the log ingestion pipeline (`api/logs.py`)
* MITRE mapping is still a 3-entry hardcoded dictionary in `services/mitre_mapper.py` — not yet a real ATT&CK dataset
* Asset risk scoring (`services/asset_risk.py`) computed live from unresolved alerts on an asset's IP, not stored/stale

## AI / ML

* **Provider abstraction implemented** (`services/ai/`): `AIProvider` interface with a `LocalProvider` (deterministic, grounded in real alert/incident/log/IOC data — no external dependency, always available) and an `OpenAIProvider` (wraps the `openai` SDK, only activates if `OPENAI_API_KEY` is set, always falls back to the local result on any API error). `GET /ai/alerts/{id}/explain` and `GET /ai/incidents/{id}/explain` use whichever provider is configured.
* `langchain`, `langgraph`, `qdrant-client`, `scikit-learn`, `pytorch` remain listed in `requirements.txt` but unused — no vector DB, no ML models, no agent framework yet.

## Reporting

* **None implemented.** `reportlab` is listed in `requirements.txt` but unused; `report_generator/` is an empty directory.

## Infrastructure

* **CI**: `.github/workflows/ci.yml` — backend tests against a real Postgres service container + `alembic upgrade head`, frontend lint/build. Runs on every push/PR to `main`.
* **No Docker** — no Dockerfile/docker-compose, no cloud deployment config.

## Testing

* **71+ tests** in `backend/tests/` (pytest + FastAPI `TestClient`, against a real disposable Postgres test database, not mocked) covering auth, RBAC, incidents, alerts, logs/detection pipeline, audit logging, assets, IOCs, and AI explanations.

---

# Planned / Future (not yet implemented — original stack plan)

These were part of the original technology plan and remain the intended direction, but nothing below exists in code yet. Treat this section as roadmap, not current state.

## Frontend

* Possible migration to Next.js 15 + TypeScript + Tailwind CSS + Shadcn UI once the feature set stabilizes

## Cache Layer

* Redis — session management, performance optimization

## AI Layer

* LangGraph for agent workflows / multi-step reasoning
* OpenAI API (GPT-4o) as the initial LLM provider, behind a provider abstraction (so Anthropic/local models can be swapped in)
* Future local/open models (Llama, Mistral) as fallback providers

## Vector Database

* Qdrant — for MITRE ATT&CK knowledge base, threat intelligence, and security playbook retrieval (RAG)

## Machine Learning

* Scikit-learn (Isolation Forest, classification) for anomaly detection
* PyTorch for future behavioral-analytics models

## Report Generation

* ReportLab for PDF executive/incident reports

## Containerization / Cloud

* Docker for consistent local/dev environments
* AWS (EC2, RDS, S3) for initial cloud deployment
* Kubernetes for future scaling

## Monitoring

* Prometheus + Grafana
* ELK stack for centralized logging

## Future Threat-Intel Integrations

* CrowdStrike, Splunk, Microsoft Sentinel, AWS CloudTrail, VirusTotal, AbuseIPDB

---

# Development Tools

* IDE: VS Code
* Version Control: Git / GitHub
* API Testing: Postman / FastAPI's built-in Swagger UI (`/docs`)
