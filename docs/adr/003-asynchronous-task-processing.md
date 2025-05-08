# ADR-003: Asynchronous Task Processing

**Date:** 2025-05-08  
**Status:** Accepted

---

## Context

The *CellSensei* application must process uploaded Jupyter notebooks to:
- Perform static analysis (AST checks, linting)
- Extract and test user-defined functions
- Run validations and return structured feedback

These tasks can be computationally intensive and variable in duration. Running them synchronously in the web request cycle would:
- Cause slow responses or browser timeouts
- Risk duplicate submissions if the user retries
- Block other users from submitting

In later phases, we expect to introduce sandboxed execution (e.g., chroot or containerized tasks), making separation of concerns and task isolation even more important.

---

## Decision

We will use **Celery** for asynchronous task processing, with **Redis** as the message broker and result backend.

---

## Alternatives Considered

### Synchronous Processing
- **Pros:** Easiest to implement; no extra infrastructure
- **Cons:** Unacceptable latency and timeout risk for real-world use

### Python Threads / `concurrent.futures`
- **Pros:** Minimal overhead; easy to prototype
- **Cons:** Not durable; no retry or queue management; can’t scale across processes

### Redis Queue (RQ), Huey, or Custom Queues
- **Pros:** Lightweight alternatives to Celery
- **Cons:** Less robust; limited async support; fewer integrations

### Serverless Functions (e.g., AWS Lambda)
- **Pros:** Scales automatically; no server maintenance
- **Cons:** Adds cloud dependency and cost; slower cold starts; limited sandbox control

### FastAPI Background Tasks
- **Pros:** Built-in async support
- **Cons:** Still tied to request context; no persistent queue

### WebSockets (for progress tracking)
- **Pros:** Great for real-time feedback
- **Cons:** Not a task runner; complements, not replaces async processing

---

## Justification

Celery with Redis was selected for the following reasons:

1. **Decoupling** – Web UI and processing logic are fully separated
2. **Scalability** – Can distribute workload across multiple workers
3. **Reliability** – Supports retries, timeouts, and robust error handling
4. **Progress Tracking** – Enables polling or updates for task status
5. **Task Management** – Offers prioritization, chaining, and scheduling
6. **Monitoring** – Comes with ecosystem tools (Flower, events, etc.)
7. **Security Isolation** – Tasks run in controlled environments, not in web threads
8. **Python Ecosystem Fit** – Compatible with our stack (FastHTML/Starlette)
9. **Future-Proofing** – Supports evolving needs (sandboxing, queue orchestration)

### Redis Justification
Redis was selected as the broker due to:
- Simplicity of setup and local dev support
- High performance for lightweight message passing
- Dual use as result backend (avoids separate DB just for task state)

---

## Consequences

- We must deploy and manage Redis and Celery workers
- Adds operational complexity (e.g., systemd services or Docker containers)
- Requires serialization of notebook metadata or paths
- Failures must be logged and surfaced properly to the UI
- Instructors/students may experience brief polling delays vs. real-time feedback

These trade-offs are acceptable and align with the 80/20 goal of scalability without overengineering.

---

## Summary

Celery and Redis form a production-grade asynchronous backend that keeps the *CellSensei* frontend responsive while enabling robust task processing. This design balances performance, security, and future extensibility while fitting comfortably within the project's Python-first philosophy.

