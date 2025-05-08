# ADR-000: Python Development Tooling and Project Configuration

**Date:** 2025-05-08  
**Status:** Accepted

---

## Context

To ensure a modern, efficient, and maintainable development process for the *CellSensei* project, a clear decision was needed regarding the Python development tooling stack — including dependency management, virtual environments, linting, formatting, type checking, testing, and documentation.

As a solo indie developer, the priorities are speed, simplicity, and alignment with current Python standards without introducing unnecessary overhead.

---

## Decision

The project will adopt the following Python development tooling:

- **Project Configuration:** Use `pyproject.toml` as the central configuration file for metadata, dependencies, and tool settings (PEP 517/518).
- **Package Management & Virtual Environments:** Use [`uv`](https://github.com/astral-sh/uv) for creating virtual environments and managing dependencies.
- **Linting & Formatting:** Use `Ruff` for both linting and formatting, replacing tools like Flake8, isort, and pyupgrade.
- **Type Checking:** Use `Mypy` for static type checking.
- **Testing Framework:** Use `Pytest` for writing and running tests.
- **Documentation:** Use `MkDocs` (Material theme) for project documentation; docstrings will be used for code-level documentation.

---

## Alternatives Considered

### Project Configuration
- `setup.py` + `requirements.txt` + separate tool config files: More fragmented and outdated compared to `pyproject.toml`.
- Multiple individual config files (`.flake8`, `.isort.cfg`, etc.): Less centralized.

### Package Management
- `pip` + `venv`: Standard, but slower and more fragmented than `uv`.
- `Poetry` and `PDM`: Powerful but considered overkill for this project’s scope.

### Linting & Formatting
- `Flake8` + `Black` + `isort`: Effective but separate tools.
- `Pylint`: Very thorough but often noisy and harder to configure.

### Type Checking
- `Pyright`: Modern and powerful, but `Mypy` is better established in the current toolchain.
- No static checking: Misses out on the benefits of type enforcement.

### Testing
- `unittest`: Verbose compared to Pytest.
- `nose2`: Less widely used and fewer plugins than Pytest.

---

## Consequences

- Developers must use tools that support `pyproject.toml` configuration.
- Some team members may need to learn newer tools (`uv`, `Ruff`) if unfamiliar.
- Adoption of `Ruff` and `uv` may reduce compatibility with older environments unless explicitly managed.

---

## Justification

This stack provides a lightweight but powerful modern Python workflow. It aligns with community standards, improves development speed, reduces cognitive load, and scales well with the project’s complexity. The use of `uv` and `Ruff` in particular accelerates install and linting workflows, making them ideal for fast iterations and continuous development.

Given the project's solo developer context, this setup balances modern best practices with simplicity and long-term maintainability.

