# SentinelAI Technology Stack

## Version

v2.0 — reconciled with actual implementation (previous version described the originally planned stack, most of which was never built; see "Planned / Future" section below for what's still aspirational).

---

# Current Implementation (as of Sprint 5)

## Frontend

* **Vite** + **React 19** (JSX, no TypeScript)
* Hand-written CSS (no Tailwind, no Shadcn UI)
* Plain `fetch()` calls to the backend, no API client library, no state management library, no router (single-page dashboard in `App.jsx`)

## Backend

* **FastAPI**
* **Python 3.13**
* **SQLAlchemy** ORM
* **Alembic** listed as a dependency but not yet used (no migrations directory / revisions exist — tables are created via `Base.metadata.create_all`)
* **python-jose** for JWT encode/decode, **passlib[bcrypt]** for password hashing

## Database

* **PostgreSQL**, connected via `DATABASE_URL` in `backend/.env` (no Redis, no caching layer)

## Security

* JWT bearer auth (`core/security.py`, `core/dependencies.py`)
* bcrypt password hashing

## AI / ML

* **None implemented.** `openai`, `langchain`, `langgraph`, `qdrant-client`, `scikit-learn`, `numpy`, `pandas` are listed in `requirements.txt` but not imported or used anywhere in `backend/app`. Threat detection today is a single hardcoded rule (failed-login count threshold) in `services/risk_engine.py`, and MITRE mapping is a 3-entry hardcoded dictionary in `services/mitre_mapper.py`.

## Reporting

* **None implemented.** `reportlab` is listed in `requirements.txt` but unused; `report_generator/` is an empty directory.

## Infrastructure

* **None.** No Dockerfile, no docker-compose, no CI/CD config, no cloud deployment config exist anywhere in the repo.

## Testing

* **None implemented.** `backend/tests/` contains only a README and a requirements file — zero test files.

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
