# CellSensei Project Roadmap

This document outlines the planned development phases and milestones for the CellSensei project.

## Guiding Principles
- Iterative development, starting with a Minimum Viable Product (MVP).
- Prioritize a responsive user experience for students.
- Implement robust security for executing student code.
- Provide valuable feedback to students, including static analysis and code quality.

## Current Status (as of YYYY-MM-DD)
- Planning Phase / Start of Milestone 1.

## Milestones

### Milestone 1: MVP - Basic Upload, Static Analysis & Synchronous Reporting (Target: ~2-3 weeks from start)
- **Goal:** Allow users to upload a notebook and receive immediate feedback from static analysis tools (AST checks, linters, formatters). No student code execution.
- **Key Features:**
    - FastHTML web application with a file upload form for `.ipynb` files.
    - Backend logic (called synchronously by FastHTML) to:
        - Receive and temporarily save the uploaded notebook.
        - Extract code from the notebook.
        - Run static analysis (custom AST checks for disallowed patterns).
        - Run linters (e.g., Ruff) and formatters (e.g., Ruff format/Black in `--check` mode).
        - Aggregate and format feedback from these tools.
    - Display the combined static analysis report directly back to the user on the webpage.
- **Technologies:** FastHTML, Uvicorn, `nbformat`, `ast`, (chosen linter/formatter tools e.g., Ruff).
- **Focus:** Core web interface, static analysis pipeline, synchronous feedback loop.

### Milestone 2: Function Extraction & Test Harness Execution (Still Synchronous, UnSANDBOXED - Primarily for Logic Validation) (Target: +2-3 weeks)
- **Goal:** Implement the logic to extract the five core student functions and test them using a predefined test harness. *This milestone focuses on validating the grading logic; execution is still synchronous and unsandboxed.*
- **Key Features:**
    - `notebook_parser.py`: Module to extract the source code of the 5 predefined core functions from the uploaded notebook.
    - `test_harness_actual/harness.py`: The Python test harness that can load the extracted function strings (e.g., via `exec()` in a controlled manner or by writing to a temp file and importing) and run predefined tests against them.
    - `assignment_defs/`: Directory to store test definitions for assignments (e.g., `weatherwise_tests.py`).
    - Update FastHTML backend: After static analysis, if successful, proceed to extract functions and run the test harness.
    - Combine test harness results with static analysis results for the report.
- **Critical Note:** Student code is executed in the web server process. This milestone should primarily use *trusted test notebooks* for development. If used with actual student submissions, it carries a security risk. The main purpose is to get the extraction and testing logic correct.

### Milestone 3: Asynchronous Processing with Celery (Target: +1-2 weeks)
- **Goal:** Decouple the time-consuming analysis and testing from the web request, making the UI responsive.
- **Key Features:**
    - Setup Celery and a message broker (e.g., Redis).
    - Refactor static analysis, function extraction, and test harness execution into a Celery task.
    - FastHTML upload route now dispatches the Celery task and returns a task ID.
    - New FastHTML endpoint (e.g., `/task_status/<task_id>`) for the frontend to poll.
    - Frontend (FastHTML + HTMX) updated to poll for status and display results asynchronously.
    - Results temporarily stored (e.g., in Redis or simple file store accessible by Celery and FastHTML).
- **Security Note:** Student code now runs in the Celery worker's process, still unsandboxed.

### Milestone 4: Sandboxed Execution with Firejail (Target: +2-3 weeks)
- **Goal:** Securely execute student code within the test harness using Firejail.
- **Key Features:**
    - Integrate Firejail into the Celery task.
    - The Celery task will invoke the `test_harness.py` (which loads/runs the student's 5 functions) via a `firejail` command using `subprocess`.
    - Configure `firejail` with appropriate restrictions (no network, private filesystem space, resource limits).
    - Ensure results from the sandboxed process are captured and reported.
- **This milestone makes the system reasonably safe for processing actual student submissions.**

### Milestone 5: Refinements, Error Handling, and UI Polish (Target: +1-2 weeks)
- **Goal:** Improve robustness, user feedback, and overall user experience.
- **Key Features:**
    - Comprehensive error handling throughout the pipeline.
    - Clearer user feedback for various states (uploading, processing, errors, success).
    - UI improvements based on initial testing.
    - Enhanced logging for easier debugging and monitoring.

### Future Considerations (Post-MVP / Beyond Current Scope)
- User accounts and submission history.
- Instructor dashboard for managing assignments and viewing results.
- More advanced static analysis or plagiarism detection.
- Configuration for different assignments directly through the UI.
- More detailed resource monitoring for Firejail processes.
