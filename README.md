# Kanban Board

Collaborative project management with drag & drop.

**Stack:** Flask (Python) · PostgreSQL · React · TypeScript · Docker

## 🚀 Quick Start
1. `make up`
2. Access at `http://localhost:3202`

## 🛠 Features
- **Board Management**: Create/manage multiple project boards.
- **Drag & Drop**: Fluid task movement across stages.
- **Member Control**: Direct member addition and removal.
- **User Assignment**: Link tasks to specific users.
- **Focus Filters**: Quick "My Tasks" toggle view.
- **Secure Auth**: JWT-protected API and frontend boundaries.

## 💻 Development
| Service | Port | Command |
| :--- | :--- | :--- |
| **Postgres** | 3200 | `make db-up` |
| **Backend** | 3201 | `make backend` |
| **Frontend** | 3202 | `make frontend` |

**Testing:** `make test`

## 🔮 Production Roadmap
- **Observability**: Distributed tracing and structured logging.
- **Alerting**: Automated error tracking and monitoring.
- **RBAC**: Fine-grained access control and permissions.
- **Security**: API Rate Limiting and Secrets Management.
- **Caching**: Redis for fast data access.
- **Workers**: Asynchronous background jobs via Celery.
- **Real-time**: WebSocket-based multi-user board synchronization.
- **DevOps**: CI/CD with automated E2E testing.
- **IaS**: Infrastructure as Code with Terraform.

Due to time constraints, focus was on core structure and UX.
