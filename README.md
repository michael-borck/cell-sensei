# CellSensei - Automated Notebook Grader

Automated feedback, static analysis, and testing for Jupyter notebooks.
This tool helps students get immediate insights into their notebook assignments
and allows educators to streamline the assessment process.

## Project Status (as of May 8, 2025)
Currently in initial development (Milestone 1: Basic Upload, Static Analysis & Synchronous Reporting).

## Features (Planned)
* Web interface for Jupyter notebook (`.ipynb`) uploads.
* Static code analysis (AST checks, linting with Ruff, formatting checks with Ruff/Black).
* Extraction and testing of 5 predefined core functions.
* Sandboxed execution of student code using Firejail.
* Asynchronous processing of submissions using Celery.
* Results and feedback displayed on the web interface (leveraging HTMX with FastHTML).

## Tech Stack
* **Web Framework:** FastHTML
* **Background Task Queue:** Celery
* **Sandboxing:** Firejail
* **Package Management & Venv:** `uv`
* **Linting/Formatting:** Ruff
* **Type Checking:** Mypy (planned)
* **Testing Framework (for app tests):** Pytest (planned)
* **Notebook Parsing:** `nbformat`

## Project Setup & Running (Milestone 1 Focus)

### Prerequisites
1.  **Git:** For cloning the repository.
2.  **Python:** Version 3.9 or higher (as specified in `pyproject.toml`).
3.  **`uv`:** The fast Python package installer and virtual environment manager.
    * If you don't have `uv` installed, you can install it via pipx, pip, or other methods. See the [official `uv` installation guide](https://github.com/astral-sh/uv#installation).
        ```bash
        # Example using pip (ensure pip is up to date)
        pip install uv
        ```

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/cellsensei.git](https://github.com/YOUR_USERNAME/cellsensei.git)
cd cellsensei
```
*(Replace `YOUR_USERNAME` with your actual GitHub username)*

### 2. Create and Activate Virtual Environment using `uv`
`uv` can create and manage virtual environments similar to `python -m venv`.

```bash
# Create a virtual environment named '.venv' in the project directory
uv venv .venv
# This will also automatically activate it if your shell is supported by 'uv venv'
# If not automatically activated, or if you open a new terminal:
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate.bat   # On Windows (Command Prompt)
# .venv\Scripts\Activate.ps1 # On Windows (PowerShell)
```
You should see `(.venv)` at the beginning of your shell prompt.

### 3. Install Dependencies using `uv`
All project dependencies, including development tools, are defined in `pyproject.toml`.
`uv pip sync` is often preferred as it ensures the environment exactly matches the lock file (if one exists and is used) or the `pyproject.toml` dependencies. For development, you'll want the `dev` optional dependencies.

```bash
# Install main dependencies and optional 'dev' dependencies
uv pip install -e ".[dev]"
# The '-e .' makes it an editable install, useful for development.
# "[dev]" installs the dependencies listed under [project.optional-dependencies.dev] in pyproject.toml.
```
Alternatively, if you prefer to sync strictly:
```bash
# (First time, or if pyproject.toml changed significantly and no lock file is committed)
# uv pip compile pyproject.toml -o requirements.lock --all-extras # To generate a lock file
# uv pip sync --all-extras requirements.lock # To install from lock file

# For simpler direct install from pyproject.toml without explicit locking step for now:
# uv pip install -e ".[dev]" works well.
```

### 4. Run the FastHTML Application
The `app.py` uses FastHTML's `serve()` function, which runs a Uvicorn server.

```bash
python app.py
```
You should see output from Uvicorn indicating the server is running, typically on `http://127.0.0.1:8000` or `http://0.0.0.0:5001`. Open this address in your web browser.

## Development

### Linting and Formatting
We use Ruff for linting and formatting, configured in `pyproject.toml`.

```bash
# Check for linting issues
uv run ruff check .

# Auto-format files
uv run ruff format .
```
*(Using `uv run` executes commands installed in the virtual environment).*

### Running Tests (Placeholder for Future Milestones)
Tests will be written using Pytest.

```bash
# (Once tests are added)
uv run pytest
```

### Type Checking (Placeholder for Future Milestones)
Mypy will be used for static type checking.

```bash
# (Once type hints are more widespread and Mypy is configured)
uv run mypy .
```

## Roadmap
See `ROADMAP.md` for the planned development phases and milestones.

## Architecture Decisions
Key architectural decisions and their rationale are documented in the `docs/adr/` directory.

