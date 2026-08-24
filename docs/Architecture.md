# SentinelAI Architecture

## Status

This document was previously empty despite the project roadmap listing it as a completed Week-1 deliverable. It now describes the actual system as implemented through Sprint 5, not an aspirational design.

---

# High-Level Structure

```
SentinelAI/
├── backend/            FastAPI application (implemented)
├── frontend/           Vite + React dashboard (implemented)
├── docs/               Product/architecture docs
├── detection_engine/   Empty — not yet built (detection logic currently
│                       lives inline in backend/app/services/risk_engine.py)
├── llm_copilot/        Empty — not yet built
├── ml_models/          Empty — not yet built
├── report_generator/   Empty — not yet built
├── synthetic_data/     Empty — no seed/demo data exists yet
└── database/           Empty — no migrations/seed scripts yet
```

The repo was previously nested one extra level (`SentinelAI/SentinelAI/...`) from an early scaffolding mistake; this has been flattened so the paths above are accurate from the repo root.

---

# Backend Structure

```
backend/app/
├── main.py                FastAPI app instantiation, CORS, router registration
├── core/
│   ├── config.py           Pydantic Settings — loads DATABASE_URL, SECRET_KEY,
│   │                       ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES from .env
│   ├── database.py         SQLAlchemy engine/session, declarative Base
│   ├── security.py         Password hashing (bcrypt) + JWT encode/decode
│   └── dependencies.py     get_current_user — FastAPI dependency that
│                           validates the bearer token on protected routes
├── models/                 SQLAlchemy ORM models: User, Log, Alert, Incident
├── schemas/                Pydantic request/response schemas
├── api/                    One router module per resource:
│   ├── auth.py              /auth/register, /auth/login (public)
│   ├── users.py             /users/me (protected)
│   ├── logs.py               /logs/upload, /logs/ (protected)
│   ├── alerts.py             /alerts/ (protected)
│   ├── incidents.py          /incidents/ CRUD + status/assign/resolve (protected)
│   ├── dashboard.py           /dashboard/stats (protected)
│   └── mitre.py                /mitre/ — hardcoded technique list (protected)
└── services/
    ├── risk_engine.py        calculate_risk(), should_generate_alert()
    └── mitre_mapper.py        map_event_to_mitre() — static event→technique dict
```

All routes except `/auth/register`, `/auth/login`, `/`, and `/health` require a
valid bearer token, verified against `SECRET_KEY` via `get_current_user`.

---

# Data Model (as implemented, not as originally designed in Database.md)

```
User
  id (UUID string, PK), name, email (unique), password_hash, role, created_at

Log
  id (int, PK), source_ip, event_type, username, risk_score, severity, created_at

Alert
  id (int, PK), source_ip, alert_type, severity, description, created_at

Incident
  id (int, PK), title, severity, status, assigned_to, resolution_notes, created_at
```

Notable gaps vs. the original `Database.md` design: no UUID PKs on
Log/Alert/Incident, no foreign keys linking Incident → Alert or Alert → Log
(everything is correlated only by matching `source_ip` strings at query
time), and none of `reports`, `investigations`, `chat_history`, or
`threat_intelligence` tables exist yet.

Tables are created via `Base.metadata.create_all(bind=engine)` on startup —
there is no Alembic migration history yet, despite Alembic being a listed
dependency.

---

# Request Flow: Log Ingestion → Alert → Incident

This is the one working end-to-end pipeline in the system today:

```
POST /logs/upload  (authenticated)
  │
  ├─ risk_engine.calculate_risk(event_type)
  │     → static if/elif lookup, e.g. "failed_login" → (85, "high")
  │
  ├─ mitre_mapper.map_event_to_mitre(event_type)
  │     → static dict lookup, e.g. "failed_login" → T1110 Brute Force
  │
  ├─ persist new Log row
  │
  └─ if event_type == "failed_login":
        count failed_login Logs with the same source_ip
        if count >= 5 (should_generate_alert):
          if no existing "Brute Force Attack" Alert for that source_ip:
            create Alert(severity="critical")
            create Incident(title="Brute Force Attack Detected", severity="critical")
              (NOT linked to the Alert via FK — created independently)
```

This is a single deterministic rule (failed-login count threshold), not a
rule engine, not a correlation engine, and not ML/AI-based despite those
being planned. It's a real, working pipeline for exactly one attack
pattern.

---

# Frontend Structure

```
frontend/src/
├── App.jsx              Single page: fetches /logs, /alerts, /incidents,
│                         /dashboard/stats, /mitre on mount; renders each
│                         as a table. No routing, no global state
│                         management, no API client abstraction (raw fetch
│                         calls with hardcoded http://127.0.0.1:8000 base URL).
├── App.css               Hand-written styling
└── components/
    ├── Sidebar.jsx        Static nav list, no routing/active-state logic
    └── Analytics.jsx       Chart.js-based component — NOT wired into
                             App.jsx, and would fail to build if imported:
                             chart.js/react-chartjs-2 are not installed.
```

There is no authentication UI yet (no login form) — the frontend does not
currently send an Authorization header, so as of this document's fixes
(all backend routes now requiring auth), the dashboard's fetch calls will
receive 401s until a login flow is added to the frontend.

---

# What's Explicitly Not Implemented

See `TechStack.md`'s "Planned / Future" section and the Sprint audit for
the full list. In architectural terms, the biggest structural gaps are:

* No AI/LLM layer of any kind (OpenAI/LangGraph/Qdrant are dependencies,
  not integrations)
* No correlation engine — every log is evaluated independently against one
  rule
* No RBAC enforcement — the `role` field exists on `User` but no endpoint
  checks it, and registration hardcodes every new user to `"analyst"`
* No asset inventory, IOC/threat-intel model, alert lifecycle beyond
  creation, or audit logging
* No background job processing — everything is synchronous within the
  request
* No tests, Docker, or CI/CD
