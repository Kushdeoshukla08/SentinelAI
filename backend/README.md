# SentinelAI Backend

FastAPI + PostgreSQL backend.

## Setup

```
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in real values:

```
DATABASE_URL=postgresql://user:password@localhost:5432/sentinelai
SECRET_KEY=<a long random string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Database

Schema is managed by Alembic migrations, not `create_all`. After creating
the database and setting `DATABASE_URL`, apply all migrations:

```
alembic upgrade head
```

To generate a new migration after changing a model in `app/models/`:

```
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## Running

```
uvicorn app.main:app --reload
```

API docs are served at `/docs` (Swagger UI) and `/redoc`.

The first user ever registered via `POST /auth/register` on a fresh
database automatically becomes `role=admin`. Every user after that
defaults to `role=analyst`; an admin can change roles via
`PATCH /users/{user_id}/role`.
