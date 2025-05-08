# ADR-000: Python Development Tooling and Project Configuration

* **Date:** 2025-05-08
* **Status:** Accepted

## Context

To ensure a modern, efficient, and maintainable development process for the "CellSensei" project, a clear decision on the Python project configuration, dependency management, virtual environment tooling, linting, formatting, type checking, and testing framework is required. The project is being developed by an indie developer, prioritizing speed, simplicity, and adherence to modern Python standards.

## Decision

The project will adopt the following Python development tooling stack:

1.  **Project Configuration:** `pyproject.toml` will be the primary file for defining project metadata, dependencies, and tool configurations, following PEP 517/518.
2.  **Package Management & Virtual Environments:** `uv` will be used for creating and managing virtual environments, and for installing/managing Python packages.
3.  **Linting & Formatting:** `Ruff` will be used for both linting (replacing tools like Flake8, isort, pyupgrade) and code formatting.
4.  **Type Checking:** `Mypy` will be used for static type checking.
5.  **Testing Framework:** `Pytest` will be used for writing and running unit and integration tests.
6.  **Documentation (Code & Project):** `MkDocs` with the Material theme is planned for project documentation (including ADRs, roadmap, user guides). Docstrings will be used for code-level documentation.

## Alternatives Considered

1.  **Project Configuration:**
    * `setup.py` + `setup.cfg` + `requirements.txt`: Traditional approach, but `pyproject.toml` is now standard and centralizes configuration.
    * Multiple separate tool configuration files (e.g., `.flake8`, `.isort.cfg`): `pyproject.toml` allows many tools to be configured in one place under `[tool.*]` sections.

2.  **Package Management & Virtual Environments:**
    * `pip` + `venv`: Standard library tools. `uv` offers significant speed improvements and a more integrated experience.
    * `Poetry`: Provides robust dependency management, packaging, and publishing. Considered more opinionated and potentially more overhead than needed for this solo project's initial scope.
    * `PDM`: Similar to Poetry, also uses `pyproject.toml` and offers modern dependency management. Also considered more feature-rich than strictly necessary for the initial phase.

3.  **Linting & Formatting:**
    * Separate tools: `Flake8` (for linting), `Black` (for formatting), `isort` (for import sorting). `Ruff` combines these functionalities into a single, extremely fast tool.
    * `Pylint`: A very thorough linter, but can be "noisier" and require more initial configuration to tune for desired feedback levels.

4.  **Type Checking:**
    * `Pyright` (by Microsoft): Another excellent type checker, often used with Pylance in VS Code. `Mypy` is the original and very widely adopted type checker in the Python ecosystem.
    * No static type checking: Forgoes the benefits of early bug detection and improved code clarity.

5.  **Testing Framework:**
    * `unittest` (Python standard library): More verbose and boilerplate-heavy compared to Pytest.
    * `Nose2`: Another testing framework. Pytest is generally more popular and has a larger ecosystem.

## Consequences / Justification

* **Adoption of `pyproject.toml`:**
    * **Pros:** Aligns with modern Python standards (PEP 517/518/621), centralizes project metadata and tool configuration, cleaner project root.
    * **Cons:** Slight learning curve if unfamiliar compared to just `requirements.txt`.
* **Use of `uv`:**
    * **Pros:** Significant speed improvements for package installation and resolution, can manage virtual environments, actively developed and gaining traction. Simplifies the developer workflow by combining roles of `pip` and `venv`.
    * **Cons:** Relatively newer tool, though it's built by a trusted team (Astral, developers of Ruff) and aims for `pip` compatibility.
* **Use of `Ruff`:**
    * **Pros:** Extremely fast, consolidates multiple linting and formatting tasks into one tool, highly configurable, excellent developer experience.
    * **Cons:** If specific plugins from Flake8 are absolutely essential and not yet covered by Ruff, that could be a gap (though Ruff's coverage is extensive and growing).
* **Use of `Mypy`:**
    * **Pros:** Enhances code quality, catches type-related errors early, improves code readability and maintainability through type hints.
    * **Cons:** Requires writing type hints, can have a learning curve, and might initially slow down development slightly until familiar.
* **Use of `Pytest`:**
    * **Pros:** Concise syntax, powerful fixture system, extensive plugin ecosystem, good for both simple and complex tests.
    * **Cons:** Third-party dependency (though widely accepted as a standard).
* **Use of `MkDocs` (with Material theme):**
    * **Pros:** Easy to write documentation in Markdown, generates professional-looking static sites, Material theme is very popular and feature-rich.
    * **Cons:** Another tool to learn if unfamiliar.

**Overall Justification:**
This chosen stack represents a modern, efficient, and productive Python development environment. The tools are generally best-in-class for their respective purposes, emphasize speed and developer experience, and integrate well with `pyproject.toml`. For a solo developer, this stack provides significant benefits without the heavy infrastructure or steep learning curves of some more enterprise-focused solutions, while still adhering to best practices. The choice of `uv` and `Ruff` specifically prioritizes development speed and a streamlined workflow.

