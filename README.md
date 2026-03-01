# Kanban Board

Collaborative project management with drag & drop task boards.

**Stack:** Flask · PostgreSQL · React · TypeScript

## Ports

| Service  | Port |
|----------|------|
| Postgres | 3200 |
| Backend  | 3201 |
| Frontend | 3202 |

## Setup

```bash
# 1. start postgres
make db-up

# 2. install deps
make install-backend
make install-frontend

# 3. run migrations
make migrate-gen msg="initial"
make migrate

# 4. start servers (in separate terminals)
make backend
make frontend
```

## Tests

```bash
make test
```

## Env Files

Copy and edit the example files:

```
backend/example.env  → backend/.env
frontend/example.env → frontend/.env
```
