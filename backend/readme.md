# Better Software Backend (Task API)

## Overview
A maintainable, modular Flask-based API for task management, built following professional software engineering patterns.

## Technical Decisions
- **Architecture**: **Layered (Controller-Service-Repository)**. Decouples business logic from HTTP transport and persistence details.
- **Data Access**: **Repository Pattern** ensures atomic database transactions via SQLAlchemy.
- **Validation**: Manual validation in controllers for simplicity, extendable via Marshmallow.
- **Traceability**: **Context-based Logging** with unique Request IDs for observability.
- **Communication**: Standardized API responses with `request_id`, `data`, and `message`.

## Structure
- `/app`: Main application package
  - `/api`: Flask Blueprints for entrypoints (v1)
  - `/controllers`: Request/Response handling
  - `/services`: Core business logic
  - `/repositories`: Data access layer
  - `/models`: Database schema using SQLAlchemy
  - `/core`: Constants, Logger, Config, and Response helpers
  - `/middleware`: Request tracing (ID)
- `/tests`: Unit tests with repository mocking
- `/run.py`: Application entrypoint

## Running Locally
1. `pip install -r requirements.txt`
2. `flask run` (or `python run.py`)

## Running Tests
- `pytest`