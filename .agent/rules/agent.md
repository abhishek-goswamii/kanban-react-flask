---
trigger: always_on
---

# Engineering Rules
  
Author: Abhishek Goswami  

This document governs both frontend and backend.
No code may violate these constraints.

---

# 1. System Boundaries

- Frontend and backend are separate systems.
- They communicate strictly via HTTP APIs.
- No shared business logic across layers.
- Backend is the source of truth.
- Frontend must treat API as untrusted boundary.

---

# 2. Backend Rules (Python + Flask)

- No business logic in route handlers.
- Domain logic lives only in service/domain layer.
- Validate all inputs using schemas.
- Never return ORM models directly.
- Reject illegal state transitions.
- Use transactions for multi-step updates.
- Use database constraints where possible.

---

# 3. Backend Testing

- Unit tests required for all domain logic.
- Unit tests must use mocks to avoid DB calls.
- No real database usage in pure unit tests.
- Test invalid transitions and failure paths.
- Tests must verify behavior, not implementation.

---

# 4. Frontend Rules (React)

- No business rules enforcement in UI.
- Never trust API responses blindly.
- Validate and guard API responses.
- Explicitly handle loading, error, and empty states.
- No direct mutation of server data.
- Keep components small and predictable.
- No hidden global state.

---

# 5. Frontend Testing

- Test critical UI flows.
- Mock API calls.
- Test failure states.
- Ensure UI reflects backend state accurately.

---

# 6. Interface Safety

- API contracts must be stable and explicit.
- Breaking changes require coordinated updates.
- All request/response structures must be typed or schema-validated.

---

# 7. Observability

- Backend logs state changes and errors.
- Frontend surfaces user-facing errors clearly.
- No silent failures anywhere in the system.

---

# 8. AI Usage Rules

AI may generate:
- Boilerplate
- Tests
- Refactors
- Documentation

AI must not:
- Introduce hidden abstractions
- Break architectural boundaries
- Skip validation
- Add unnecessary complexity

All AI-generated code must be reviewed and simplified.

---

# 9. Change Resilience

- New features must not cause widespread modification.
- Existing behavior must remain verifiable via tests.
- If small changes require large rewrites, architecture must be reconsidered.

---

# 10. Definition of Done

A feature is complete only when:

- Backend rules enforced
- Frontend guards implemented
- Unit tests exist (with mocks)
- Invalid states prevented
- Errors observable