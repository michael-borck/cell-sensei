# ADR-002: Choice of Web Framework

**Date:** 2025-05-08  
**Status:** Accepted

---

## Context

The *CellSensei* project requires a simple web interface to allow students to upload Jupyter notebooks and receive automated feedback. This interface must support:
- Secure file uploads
- Dynamic status and result updates
- Seamless integration with Python-based analysis and grading logic

Additional considerations:
- The project is developed by a solo developer, so simplicity and minimal context switching are important.
- Staying in Python (avoiding the need for JavaScript frameworks or templating DSLs) was a key goal.
- Resource constraints make performance and dev-efficiency critical — overengineering is a risk.

---

## Decision

We have chosen **FastHTML** as the web framework for *CellSensei*.

---

## Alternatives Considered

### Flask
- ✅ Simple, minimal, well-documented
- ⚠️ Requires Jinja templates and explicit route wiring
- ⚠️ HTMX integration is possible, but requires more manual setup
- ⚠️ Adds boilerplate for form handling, file uploads, and async patterns

### Django
- ✅ Feature-rich, includes ORM, admin panel, templating engine
- ⚠️ Overkill for a small-scale tool
- ⚠️ Steep learning curve and opinionated structure
- ⚠️ More suited to multi-user systems or content-heavy platforms

### FastAPI
- ✅ High-performance, async-native, automatic OpenAPI docs
- ✅ Clean routing and dependency injection
- ⚠️ Focused on APIs — not HTML rendering
- ⚠️ Requires a separate frontend stack (e.g., React, Vue, or HTMX manually)
- ⚠️ Breaks the “one language” goal for UI unless HTMX is layered on manually

### Quarto
- ✅ Great for scientific publishing and rendering notebooks
- ⚠️ Not a general-purpose web framework
- ⚠️ Better suited to producing static or reactive documents, not interactive upload/response apps

---

## Justification

### Simplicity and Alignment
FastHTML allows building interactive, server-rendered pages using only Python. This reduces mental overhead, improves clarity, and removes the need for a separate templating or JS language.

### Lightweight but Capable
It avoids the boilerplate of Flask and the complexity of Django, while still offering structured components, routing, and HTMX-ready responses — all built on **Starlette**, which supports async out of the box.

### Unified Python Stack
Choosing FastHTML lets us keep the project 100% Python — from frontend rendering to backend notebook parsing. This reduces tooling friction and aligns with the project's educational focus.

### Clear Progressive Path
HTMX support means we can start with basic synchronous feedback and add asynchronous interactions incrementally (e.g., polling task status). This avoids premature complexity while enabling growth.

---

## Consequences

- The project avoids frontend JavaScript frameworks or custom SPA builds.
- UI components and feedback logic are all written in Python, reducing complexity.
- We forego Django’s built-in admin and ORM features — but these aren’t needed for the MVP.
- We rely on the growing (but smaller) FastHTML ecosystem.

**Summary**:  
FastHTML strikes a strong balance between power and simplicity for *CellSensei*. It avoids unnecessary frontend tooling, encourages modular development, and stays within Python’s ecosystem — all while enabling dynamic web interaction with minimal effort.
