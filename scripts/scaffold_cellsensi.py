import os

BASE_DIR = "cell-sensei"

# Define the directory structure and files
structure = {
    ".gitignore": "",
    "README.md": "# CellSensei\n\nAutomated grading framework for notebooks.\n",
    "requirements.txt": "# Add your Python dependencies here\nfastapi\nuvicorn\ncelery\nnbformat\n",
    "config.py": "# Optional configuration file\n",

    "main_app.py": (
        "# Main FastHTML application entry point\n"
        "if __name__ == '__main__':\n"
        "    import uvicorn\n"
        "    uvicorn.run('web_ui.routes:app', host='0.0.0.0', port=8000, reload=True)\n"
    ),

    "web_ui/__init__.py": "",
    "web_ui/routes.py": (
        "# Define FastHTML routes here\n"
        "from fastapi import APIRouter\n"
        "app = APIRouter()\n"
    ),
    "web_ui/components.py": "# Optional reusable FastHTML components\n",

    "sensei_core/__init__.py": "",
    "sensei_core/static_analyzer.py": "# Static code analysis logic (e.g., linting)\n",
    "sensei_core/notebook_parser.py": "# Logic for parsing notebooks and extracting functions\n",
    "sensei_core/test_runner.py": "# Executes test harness logic on student functions\n",

    "test_harness_actual/__init__.py": "",
    "test_harness_actual/harness.py": "# Contains test harness logic\n",

    "assignment_defs/weatherwise_tests.py": "# Predefined tests for WeatherWise assignment\n",

    "celery_worker/__init__.py": "",
    "celery_worker/app.py": "# Celery application instance\n",
    "celery_worker/tasks.py": "# Celery tasks for background processing\n",
    "celery_worker/celeryconfig.py": "# Configuration for Celery\n",

    "scripts/run_firejail_test.sh": "#!/bin/bash\n# Example script for running Firejail tests\n"
}

def scaffold_project():
    for path, content in structure.items():
        full_path = os.path.join(BASE_DIR, path)
        dir_path = os.path.dirname(full_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        if full_path.endswith(".sh"):
            os.chmod(full_path, 0o755)  # Make shell scripts executable

    print(f"Project '{BASE_DIR}' scaffolded successfully.")

if __name__ == "__main__":
    scaffold_project()

