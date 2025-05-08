# ADR-007: Feedback Report Format and Delivery

**Date:** 2025-05-08  
**Status:** Accepted

---

## Context

The *CellSensei* system performs multiple stages of analysis on student-submitted Jupyter notebooks, including:

- Static analysis (AST rules, linting, formatting)
- Function extraction checks
- Test harness execution
- Sandbox compliance (if applicable)

These stages generate valuable insights, errors, and suggestions — but without a consistent report format, students could be confused or overwhelmed. The report must:

- Help students understand what worked, what didn’t, and why
- Support formative learning (not just summative judgment)
- Be readable in the browser (via FastHTML/HTMX) and optionally downloadable (e.g., as JSON or PDF)
- Separate technical logs from actionable feedback

---

## Decision

Feedback will be generated as a **structured report document**, with the following properties:

- Rendered to HTML using Python templates (FastHTML/HTMX)
- Backed by a well-defined **internal JSON structure**
- Includes color-coded sections and severity icons
- Clearly separates:
  - Analysis phase (structure/safety/style)
  - Execution phase (function test results)
  - Metadata (filename, submission time, task ID, etc.)
- Available immediately via the web interface (HTMX update)
- Optionally downloadable (JSON first, PDF later)

---

## Report Structure (Internal Format)

The internal feedback report will be structured as a JSON object like:

```json
{
  "submission": {
    "filename": "weatherwise_submission.ipynb",
    "submitted_at": "2025-05-08T12:34:56Z",
    "task_id": "abc123"
  },
  "static_analysis": [
    {
      "type": "error",
      "message": "Function name mismatch: expected `calculate_total`, found `calcTotal`.",
      "hint": "Use the exact function name defined in the assignment."
    },
    {
      "type": "warning",
      "message": "No docstring provided for `calculate_average`.",
      "hint": "Docstrings help document your code."
    }
  ],
  "test_results": [
    {
      "function": "calculate_total",
      "status": "pass",
      "message": "All tests passed."
    },
    {
      "function": "calculate_average",
      "status": "fail",
      "message": "Expected 3.5, got 4.2"
    }
  ],
  "sandbox_status": {
    "execution_safe": true,
    "firejail_profile": "default",
    "runtime": "0.91s"
  },
  "summary": {
    "errors": 1,
    "warnings": 1,
    "tests_passed": 1,
    "tests_failed": 1
  }
}
````

---

## Rendering Format (Frontend)

This JSON is rendered to HTML using FastHTML templates + HTMX fragments. Features include:

* ✅ Collapsible sections for each phase (Static Analysis, Tests, System)
* ✅ Color and icon indicators:

  * ✅ Green (pass), ⚠️ Yellow (warning), ❌ Red (error)
* ✅ HTMX auto-refresh for async processing (polling until complete)
* ✅ Actionable hints and (optional) links to docs or rubrics
* ✅ Future support: shareable link or downloadable JSON

---

## Justification

### Learner-Centered Design

* The structure promotes clarity over verbosity.
* Students see exactly *what failed*, *why*, and *how to improve*.
* Severity icons + color-coding support fast scanning under stress.

### Technical Decoupling

* The internal JSON structure decouples rendering logic from grading logic.
* Makes future delivery channels (e.g., PDFs, LMS integrations) easier to implement.

### Immediate Feedback, Minimal Overhead

* Feedback is rendered inline without requiring full-page reloads.
* HTMX ensures dynamic updates feel snappy without JavaScript build complexity.

---

## Consequences

* Requires maintaining a lightweight templating system and structured feedback spec
* More complex than returning a plain string or dumping logs
* Template bugs could misrepresent the student’s actual performance

These risks are worth it to ensure that *feedback* — not grading — is the core student value.

---

## Future Considerations

* PDF/Markdown export for offline viewing or LMS upload
* Analytics (e.g., tracking common student mistakes over time)
* Instructor-customizable rubrics per assignment
* Internationalization / localization for non-English learners

---

## Summary

*CellSensei* will use a structured, extensible feedback report format rendered to HTML via FastHTML. The design ensures transparency, educational value, and future adaptability, supporting the project's mission of “feedback-first” notebook assessment.

