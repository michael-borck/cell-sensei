# ADR-005: Static Analysis Approach

**Date:** 2025-05-08  
**Status:** Accepted

---

## Context

The *CellSensei* system must evaluate Jupyter notebooks submitted by students. These notebooks are often inconsistent, may include hidden errors, and in many cases, contain structural or stylistic issues that can hinder grading or learning outcomes.

To address these challenges **before execution**, the project implements a static analysis phase that:
- Pre-screens notebooks for safety and correctness
- Extracts the core student-defined functions
- Provides early, formative feedback to students
- Improves downstream reliability of testing and sandboxing

This analysis must be lightweight, fast, and consistent across submissions — ideally providing immediate and actionable insights.

---

## Decision

*CellSensei* will implement a **multi-layered static analysis pipeline** using:

1. **AST-based custom rules** (via `ast` module and `astroid`)
2. **Linters and formatters** (`ruff`, `black`, `isort`)
3. **Structural heuristics** for function names, argument counts, docstrings, etc.
4. **Safety checks** for disallowed modules, file access, or suspicious patterns

This occurs before sandboxing or testing.

---

## Analysis Steps

### 1. Notebook Parsing (`nbformat`)
- Jupyter notebooks are parsed using the `nbformat` library.
- All code cells are extracted and concatenated into a single logical Python script.
- Metadata (e.g., kernel type, cell count) may be logged for reference.

### 2. AST Inspection (Custom Rules)
- The combined code is parsed using Python’s `ast` module.
- A custom visitor walks the tree and collects:
  - Function definitions
  - Imports
  - Assignments
  - Forbidden constructs (e.g., `eval`, `exec`, `__import__`)
- This step builds a structured representation of what the student wrote, including:
  - Names and arguments of top-level functions
  - Use of recursion, global variables, or mutation
  - Complexities (e.g., nested `if`, deeply nested loops)

### 3. Code Hygiene Checks
- Code is passed through `ruff` to detect:
  - Syntax errors
  - Unused imports
  - Shadowed variables
  - Overly complex expressions
  - Style violations (PEP8, pyflakes, etc.)
- Optional: `black` or `isort` may be run in “check-only” mode to verify formatting consistency

### 4. Heuristic Validation
- Specific rubric-based checks are applied:
  - Were exactly 5 expected functions defined?
  - Did function names match the expected signature?
  - Were they defined at top-level (not nested)?
  - Were default arguments or type hints used?
  - Did each function include a docstring?

These checks help catch cases like:
- A student defining their solution in a comment block or markdown cell
- Partial/incomplete function definitions
- Logic spread across cells, making extraction unreliable

### 5. Safety Filters
- Any notebook that includes the following is flagged or rejected:
  - Use of `os`, `subprocess`, `shutil`, or `socket`
  - File I/O (`open`, `write`, `delete`)
  - Dynamic imports, `eval`, `exec`, or `compile`
  - Attempts to create GUI windows, launch threads, etc.
- Optionally: checks for resource abuse (e.g., loops with no exit condition)

---

## Feedback to Students

Feedback is structured in a report (JSON or rendered HTML), with sections like:

```

❌ Function Name Mismatch: Expected `def calculate_total()`, found `def calcTotal()`
✅ 5 Functions Found: All required definitions present
⚠️ Missing Docstrings: Only 2 of 5 functions include a docstring
✅ No Disallowed Imports Detected
❌ Style Errors: 12 issues found via Ruff

```

Each item includes:
- Severity (❌ error, ⚠️ warning, ✅ pass)
- Message
- (Optionally) Suggested fix or link to documentation

This ensures students:
- Understand *why* their submission failed to progress
- Get early guidance on readability, maintainability, and correctness
- Have a clear path to revision without trial-and-error submission

---

## Justification

### Safety
Static analysis is the **first layer of defense** — rejecting malicious or malformed submissions before any code is executed. Combined with sandboxing, this creates a secure processing pipeline.

### Education
Feedback on style, structure, and completeness supports the project’s pedagogical goals. Students learn not just *whether* their solution works, but how it *should be written*.

### Reliability
Well-structured, extracted functions improve the robustness of the test harness phase. Static checks reduce downstream errors and false negatives.

---

## Consequences

- A minor increase in processing time per submission (~0.5–1s)
- Need to maintain a custom AST visitor and linter ruleset
- Some students may struggle with “soft fails” (e.g., minor style issues)
- Edge cases (e.g., obfuscated but technically valid code) may require fallback handling

These are manageable trade-offs given the benefits to security, UX, and instructional value.

---

## Future Considerations

- Provide a “preview” button so students can run static checks before submitting
- Extend rules with custom plugins (e.g., `flake8`-style validators)
- Add visual inline annotations (à la CodeGrade or GitHub Suggestions)
- Log anonymized data to track common student mistakes over time

---

## Summary

The *CellSensei* static analysis system provides early, actionable feedback using a combination of:
- AST parsing
- Linting
- Safety filters
- Custom heuristics

This reduces execution risk, improves test reliability, and reinforces clean code practices — making it a core feature of the feedback workflow.
