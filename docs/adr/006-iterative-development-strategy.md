# ADR-006: Iterative Development Strategy

**Date:** 2025-05-08  
**Status:** Accepted

---

## Context

The *CellSensei* project is designed to help students receive immediate, automated feedback on their Jupyter notebook assignments. To achieve this without overengineering or creating unmaintainable code, the project follows a **milestone-based, iterative development model** guided by:

- A single developer’s time and resource constraints
- A need to release early and test often
- Evolving security and feedback requirements
- The principle of delivering educational value with each layer of refinement

Each milestone builds on the last, progressing from static analysis to secure execution, while keeping the core goal of **feedback-first, secure-enough processing** in view.

---

## Decision

The project will follow a **five-milestone iterative roadmap**, starting with a working prototype (MVP) and expanding incrementally toward a full-featured, secure submission processing system.

Each milestone introduces one or more core features while maintaining:
- Simplicity and deployability
- Feedback loops for testing and refinement
- Clear boundaries between frontend (FastHTML) and backend (analysis and sandboxing)

---

## Milestone Overview

### ✅ Milestone 1: Static Analysis MVP
- Upload `.ipynb` via FastHTML
- Extract notebook code and run static analysis:
  - AST checks
  - Linting with Ruff
  - Formatting validation (Ruff/Black in check-only mode)
- Return synchronous feedback (no code execution yet)

### 🔄 Milestone 2: Function Extraction & Test Harness
- Extract the 5 required student functions using `notebook_parser.py`
- Validate function structure and names
- Run predefined tests using `test_harness.py` (still synchronously, unsandboxed)
- Primarily used with trusted notebooks during development

### 🔄 Milestone 3: Asynchronous Processing (Celery)
- Introduce Celery and Redis for background task queuing
- Dispatch grading tasks asynchronously
- Add a `/task_status/<task_id>` endpoint for polling
- Integrate HTMX to improve frontend responsiveness

### 🔒 Milestone 4: Sandboxed Execution (Firejail)
- Secure student code execution using `firejail` + `venv`
- Enforce filesystem and network restrictions
- Refactor Celery tasks to run test harness inside Firejail using `subprocess`

### 🎨 Milestone 5: UI & Error Handling Refinement
- Improve frontend clarity (upload, pending, complete, error states)
- Add logging and debugging hooks
- Enhance user messages and recoverable failure reporting

---

## Justification

This strategy was chosen based on several guiding factors:

### 🔄 Incremental Risk Management
- Static analysis (Milestone 1) ensures no code is executed until its safety is verified.
- Execution only occurs in trusted, synchronous mode in Milestone 2.
- Full async and sandboxed workflows are introduced only after safety and stability are validated.

### 💡 Feedback-First Design
- Every milestone provides meaningful user feedback, even in the MVP stage.
- Feedback is not an afterthought but a core design feature, aligned with educational goals.

### 👤 Single-Developer Scope
- The roadmap acknowledges realistic limits of a solo developer (time, infrastructure).
- Avoids premature abstraction or overengineering.
- Ensures continuous value delivery and testable outputs.

### 💥 Fail-Safe Growth
- Each milestone can be independently tested and reverted if necessary.
- Task queue isolation and modular harnesses reduce blast radius of breaking changes.

---

## Consequences

- Not all features (e.g., sandboxing, retry logic, resource quotas) are available from day one
- Early versions must be deployed cautiously (e.g., Milestone 2 cannot be exposed to real student input)
- Test coverage must evolve alongside milestone complexity
- Developers must maintain backward compatibility or cleanup logic between iterations (e.g., result formats, temporary folder structure)

These trade-offs are acceptable in exchange for a safe, sustainable build-up of functionality.

---

## Summary

*CellSensei* is developed through five well-scoped milestones that gradually increase system capabilities while maintaining safety, clarity, and feedback value. This iterative strategy supports early validation, modular expansion, and reliable growth — crucial for a solo-developed, education-focused tool.

