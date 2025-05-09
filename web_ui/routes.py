from fasthtml.common import *
from fasthtml.components import Form # Explicit import if not in common needed for this
import nbformat # For reading notebook in M1 for static analysis
from starlette.datastructures import UploadFile
from starlette.requests import Request # For type hinting if needed
from pathlib import Path
import yaml

# Import our function extraction and testing modules
from sensei_core.notebook_parser import extract_functions_from_file, get_available_configs, test_extracted_functions

# Assuming main_app.py creates `app` and we add routes to it.
# This requires a bit of coordination or passing the app/router instance.
# For now, let's define an init_routes function.

# A global router if you prefer defining routes on it directly and then including in app
# from fasthtml.routing import APIRouter
# rt = APIRouter()
# Then in main_app.py: app.include_router(rt)

# For now, let's assume we get the app object and attach routes.
def init_routes(app):
    # In a real app, move UPLOAD_DIR to a config or pass it around.
    UPLOAD_DIR = Path("./temp_uploads")

    @app.route("/", methods=["GET"])
    async def homepage(req: Request):
        # Enhanced styling based on the mockup
        css = Style("""
            body {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                min-height: 100vh;
                background: linear-gradient(to bottom right, #1a1a2e, #16213e);
                color: #f0f0f0;
                padding: 1.5rem;
                margin: 0;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            
            .header {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 2rem;
            }
            
            .logo-container {
                background-color: rgba(236, 72, 153, 0.2);
                padding: 0.5rem;
                border-radius: 0.5rem;
            }
            
            .logo {
                width: 2rem;
                height: 2rem;
                background: linear-gradient(to right, #ec4899, #8b5cf6);
                border-radius: 0.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.25rem;
            }
            
            .title {
                font-size: 1.5rem;
                font-weight: bold;
                background: linear-gradient(to right, #a78bfa, #ec4899);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }
            
            .card {
                background-color: rgba(31, 41, 55, 0.5);
                backdrop-filter: blur(4px);
                border-radius: 0.75rem;
                padding: 1.5rem;
                border: 1px solid rgba(75, 85, 99, 0.5);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                margin-bottom: 1.5rem;
            }
            
            .card-title {
                font-size: 1.25rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 1rem;
                color: #f0f0f0;
            }
            
            .subtitle {
                font-size: 0.875rem;
                color: #9ca3af;
                margin-bottom: 1rem;
            }
            
            .drop-zone {
                border: 2px dashed rgba(75, 85, 99, 0.7);
                border-radius: 0.5rem;
                padding: 2rem;
                text-align: center;
                cursor: pointer;
                transition: border-color 0.3s;
                background-color: rgba(31, 41, 55, 0.5);
                margin-bottom: 1rem;
            }
            
            .drop-zone:hover {
                border-color: #8b5cf6;
            }
            
            .file-icon {
                font-size: 2rem;
                color: #8b5cf6;
                margin-bottom: 0.5rem;
            }
            
            .drop-text {
                color: #d1d5db;
                font-weight: 500;
            }
            
            .drop-subtext {
                font-size: 0.75rem;
                color: #6b7280;
                margin-top: 0.25rem;
            }
            
            .check-category {
                background-color: rgba(31, 41, 55, 0.7);
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            .category-header {
                font-weight: 500;
                color: #d1d5db;
                margin-bottom: 0.75rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .category-icon {
                color: #8b5cf6;
            }
            
            .check-row {
                display: flex;
                align-items: center;
                margin-bottom: 0.75rem;
            }
            
            .check-label {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                cursor: pointer;
                flex: 1;
            }
            
            .custom-checkbox {
                width: 1.25rem;
                height: 1.25rem;
                border-radius: 0.25rem;
                border: 1px solid #4b5563;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background-color 0.3s;
            }
            
            input[type="checkbox"]:checked + .custom-checkbox {
                background-color: #8b5cf6;
                border-color: #8b5cf6;
            }
            
            .check-text {
                font-size: 0.875rem;
                color: #d1d5db;
            }
            
            .info-icon {
                color: #6b7280;
                cursor: pointer;
                transition: color 0.3s;
            }
            
            .info-icon:hover {
                color: #8b5cf6;
            }
            
            .tooltip {
                position: absolute;
                right: 2rem;
                top: 0;
                width: 16rem;
                background-color: #111827;
                padding: 0.75rem;
                border-radius: 0.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                font-size: 0.75rem;
                z-index: 10;
                border: 1px solid #374151;
            }
            
            .analyze-btn {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                background: linear-gradient(to right, #8b5cf6, #6366f1);
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                font-weight: 500;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                border: none;
                color: white;
                cursor: pointer;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .analyze-btn:hover {
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }
            
            .hidden {
                display: none;
            }
        """)
        
        # Define the check categories according to the mockup
        check_categories = [
            {
                "name": "Code Quality",
                "icon": "💻",
                "checks": [
                    {"id": "check_style", "label": "Style Guide Compliance", 
                     "description": "Checks adherence to PEP 8 and common style conventions", "default": True},
                    {"id": "check_linter", "label": "Linter Checks", 
                     "description": "Identifies potential errors and bad practices", "default": True},
                    {"id": "check_unused", "label": "Unused Variables", 
                     "description": "Detects variables that are defined but never used", "default": True},
                    {"id": "check_complexity", "label": "Complexity Analysis", 
                     "description": "Evaluates cyclomatic complexity and code maintainability", "default": False}
                ]
            },
            {
                "name": "Documentation & Safety",
                "icon": "🛡️",
                "checks": [
                    {"id": "check_security", "label": "Security Vulnerabilities", 
                     "description": "Identifies potential security issues in your code", "default": True},
                    {"id": "check_docstrings", "label": "Docstring Coverage", 
                     "description": "Checks for missing or incomplete docstrings", "default": True}
                ]
            },
            {
                "name": "Best Practices",
                "icon": "✨",
                "checks": [
                    {"id": "check_best_practices", "label": "Best Practices", 
                     "description": "Enforces Python best practices and design patterns", "default": True},
                    {"id": "check_mypy", "label": "Type Checking", 
                     "description": "Validates type annotations and detects potential type errors", "default": False}
                ]
            }
        ]
        
        # Add CSS for nested accordions
        accordion_css = Style("""
            /* Main accordion styles */
            .accordion-container {
                width: 100%;
            }
            
            .accordion-item {
                margin-bottom: 0.75rem;
                border-radius: 0.5rem;
                overflow: hidden;
            }
            
            .accordion-header {
                padding: 0.75rem 1rem;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background-color 0.3s;
                border-radius: 0.5rem;
            }
            
            .accordion-header-text {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 500;
            }
            
            .accordion-content {
                padding: 1rem;
                border-bottom-left-radius: 0.5rem;
                border-bottom-right-radius: 0.5rem;
                display: none;
            }
            
            /* Parent accordion styles */
            .parent-accordion .accordion-header {
                background-color: rgba(31, 41, 55, 0.7);
            }
            
            .parent-accordion .accordion-header:hover {
                background-color: rgba(55, 65, 81, 0.7);
            }
            
            .parent-accordion .accordion-content {
                background-color: rgba(31, 41, 55, 0.5);
            }
            
            /* Child accordion styles */
            .child-accordion .accordion-header {
                background-color: rgba(45, 55, 72, 0.7);
                margin-bottom: 0.5rem;
            }
            
            .child-accordion .accordion-header:hover {
                background-color: rgba(55, 65, 81, 0.9);
            }
            
            .child-accordion .accordion-content {
                background-color: rgba(45, 55, 72, 0.5);
                padding: 0.75rem;
                margin-bottom: 0.75rem;
            }
            
            /* Animation for accordion */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .accordion-content.visible {
                display: block;
                animation: fadeIn 0.3s ease-in-out;
            }

            /* Recommended checks section */
            .recommended-checks {
                background-color: rgba(31, 41, 55, 0.7);
                padding: 0.75rem 1rem;
                border-radius: 0.5rem;
                margin-bottom: 0.75rem;
            }
            
            /* Custom native checkbox styling for recommended checkbox */
            #recommended_checks {
                appearance: none;
                -webkit-appearance: none;
                width: 1.25rem;
                height: 1.25rem;
                border: 1px solid #8b5cf6;
                border-radius: 0.25rem;
                margin-right: 0.75rem;
                position: relative;
                cursor: pointer;
                outline: none;
                display: inline-block;
                vertical-align: middle;
                background-color: rgba(139, 92, 246, 0.1);
            }
            
            #recommended_checks:checked {
                background-color: #8b5cf6;
            }
            
            #recommended_checks:checked::after {
                content: "✓";
                position: absolute;
                color: white;
                font-size: 0.9rem;
                font-weight: bold;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }
        """)

        # Generate the check options UI with nested accordions
        
        # Create child accordions (one for each category)
        child_accordions = []
        
        for i, category in enumerate(check_categories):
            category_checks = []
            
            for check in category["checks"]:
                # Create a check row with tooltip
                check_row = Div(
                    Div(
                        Label(
                            Input(type="checkbox", name=check["id"], id=check["id"], 
                                  checked=check["default"], cls="sr-only"),
                            Div(cls="custom-checkbox"),
                            Span(check["label"], cls="check-text"),
                            cls="check-label"
                        ),
                        cls="flex-1"
                    ),
                    Div(
                        "ℹ️",
                        cls="info-icon",
                        title=check["description"]
                    ),
                    cls="check-row relative"
                )
                category_checks.append(check_row)
            
            # Create a child accordion for this category
            child_accordion = Div(
                Div(
                    Div(
                        Span(category["icon"], style="color: #8b5cf6;"),
                        category["name"],
                        cls="accordion-header-text"
                    ),
                    Span("▼", id=f"child_accordion_arrow_{i}"),
                    cls="accordion-header",
                    onclick=f"""
                        const content = document.getElementById('child_accordion_content_{i}');
                        const arrow = document.getElementById('child_accordion_arrow_{i}');
                        
                        if (content.classList.contains('visible')) {{
                            content.classList.remove('visible');
                            arrow.textContent = '▼';
                        }} else {{
                            content.classList.add('visible');
                            arrow.textContent = '▲';
                        }}
                    """
                ),
                Div(
                    *category_checks,
                    id=f"child_accordion_content_{i}",
                    cls="accordion-content"
                ),
                cls="accordion-item child-accordion"
            )
            
            child_accordions.append(child_accordion)
        
        # Create a parent accordion that contains all child accordions
        parent_accordion = Div(
            Div(
                Div(
                    Span("⚙️", style="color: #8b5cf6;"),
                    "Advanced Configuration",
                    cls="accordion-header-text"
                ),
                Span("▼", id="parent_accordion_arrow"),
                cls="accordion-header",
                onclick=f"""
                    const content = document.getElementById('parent_accordion_content');
                    const arrow = document.getElementById('parent_accordion_arrow');
                    
                    if (content.classList.contains('visible')) {{
                        content.classList.remove('visible');
                        arrow.textContent = '▼';
                    }} else {{
                        content.classList.add('visible');
                        arrow.textContent = '▲';
                    }}
                """
            ),
            Div(
                Div(
                    "Configure specific checks for your code analysis. Expand each category to see available options.",
                    style="font-size: 0.875rem; color: #9ca3af; margin-bottom: 1rem;"
                ),
                *child_accordions,
                id="parent_accordion_content",
                cls="accordion-content"
            ),
            cls="accordion-item parent-accordion"
        )
        
        # Create the recommended checks section (always visible)
        recommended_checks = Div(
            Div(
                Label(
                    Input(type="checkbox", id="recommended_checks", checked=True),
                    Span("Use recommended settings", cls="check-text"),
                    cls="check-label",
                    style="margin-bottom: 0.5rem; display: flex; align-items: center;"
                )
            ),
            Div(
                "Enables a carefully selected set of checks appropriate for most student code. Uncheck to use custom settings below.",
                style="font-size: 0.8rem; color: #9ca3af;"
            ),
            cls="recommended-checks"
        )
        
        # Combine all elements
        check_options_elements = [
            accordion_css,
            recommended_checks,
            parent_accordion
        ]
        
        # Create the main upload card
        upload_card = Div(
            Div(
                Span("📤", cls="card-title-icon"),
                "Upload Your Python Code",
                cls="card-title"
            ),
            Div(
                "Accepts Jupyter Notebooks (.ipynb) or Python Scripts (.py)",
                cls="subtitle"
            ),
            Label(
                Input(type="file", name="notebook_file", id="file-upload", accept=".ipynb,.py", cls="hidden"),
                Div(
                    Div(
                        Span("📄", cls="file-icon"),
                        P("Drag & drop your file here or click to browse", cls="drop-text"),
                        P("Max file size: 10MB", cls="drop-subtext", id="file-info")
                    )
                ),
                cls="drop-zone",
                id="drop-zone"
            ),
            cls="card"
        )
        
        # Function testing section
        function_test_section = ""
        
        # Get available test configurations
        available_configs = get_available_configs()
        
        if available_configs:
            config_options = []
            
            # Create config options
            for config in available_configs:
                config_name = config.get("name", "Unnamed Configuration")
                config_path = config.get("file_path", "")
                
                config_option = Option(
                    config_name,
                    value=config_path
                )
                config_options.append(config_option)
            
            # Create the function test accordion
            function_test_section = Div(
                Div(
                    Div(
                        Span("🧪", style="color: #8b5cf6;"),
                        "Function Testing",
                        cls="accordion-header-text"
                    ),
                    Span("▼", id="function_test_arrow"),
                    cls="accordion-header",
                    onclick=f"""
                        const content = document.getElementById('function_test_content');
                        const arrow = document.getElementById('function_test_arrow');
                        
                        if (content.classList.contains('visible')) {{
                            content.classList.remove('visible');
                            arrow.textContent = '▼';
                        }} else {{
                            content.classList.add('visible');
                            arrow.textContent = '▲';
                        }}
                    """
                ),
                Div(
                    Div(
                        "Test specific functions against predefined test cases",
                        style="font-size: 0.875rem; color: #9ca3af; margin-bottom: 1rem;"
                    ),
                    Div(
                        Label(
                            Input(type="checkbox", name="run_function_tests", id="run_function_tests"),
                            Div(cls="custom-checkbox"),
                            Span("Enable Function Testing", cls="check-text"),
                            cls="check-label"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    Div(
                        Div(
                            "Select a Test Configuration:",
                            style="margin-bottom: 0.5rem; font-size: 0.875rem;"
                        ),
                        Select(
                            *config_options,
                            name="test_config",
                            id="test_config",
                            disabled=True,
                            style="width: 100%; padding: 0.5rem; border-radius: 0.25rem; background-color: rgba(31, 41, 55, 0.7); color: #d1d5db; border: 1px solid rgba(75, 85, 99, 0.7);"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    Div(
                        "Functions will be detected and displayed for selection after upload.",
                        style="font-size: 0.75rem; color: #9ca3af; font-style: italic;"
                    ),
                    id="function_test_content",
                    cls="accordion-content"
                ),
                cls="accordion-item child-accordion",
                style="margin-top: 1rem;"
            )
        
        # Configuration card
        config_card = Div(
            Div(
                Span("⚙️", cls="card-title-icon"),
                "Configure Analysis",
                cls="card-title"
            ),
            *check_options_elements,
            function_test_section if available_configs else "",
            Div(
                Button(
                    Span("▶️", style="margin-right: 0.5rem;"),
                    "Analyze Code",
                    cls="analyze-btn",
                    type="submit"
                ),
                style="display: flex; justify-content: center; margin-top: 1.5rem;"
            ),
            cls="card"
        )
        
        # Main upload form
        upload_form = Form(
            upload_card,
            config_card,
            action="/upload", 
            method="post", 
            enctype="multipart/form-data"
        )
        
        # JavaScript for the UI enhancements with minimal JS
        script = Script("""
            // Handle file selection display
            document.getElementById('file-upload').addEventListener('change', function(e) {
                const fileInfo = document.getElementById('file-info');
                if (this.files.length > 0) {
                    const file = this.files[0];
                    const dropZone = document.getElementById('drop-zone');
                    
                    // Update the drop zone text
                    const dropText = dropZone.querySelector('.drop-text');
                    dropText.textContent = file.name;
                    
                    // Update file info
                    const fileSizeKB = (file.size / 1024).toFixed(2);
                    fileInfo.textContent = `${fileSizeKB} KB`;
                    
                    // Highlight the drop zone
                    dropZone.style.borderColor = '#8b5cf6';
                }
            });
            
            // Handle the recommended checks checkbox
            const recommendedCheckbox = document.getElementById('recommended_checks');
            if (recommendedCheckbox) {
                // Function to update custom check visibility
                const updateCustomChecksVisibility = () => {
                    const parentAccordion = document.querySelector('.parent-accordion');
                    if (parentAccordion) {
                        if (recommendedCheckbox.checked) {
                            // Disable and gray out the advanced config section when using recommended settings
                            parentAccordion.style.opacity = '0.5';
                            parentAccordion.style.pointerEvents = 'none';
                            
                            // Collapse the parent accordion if it's open
                            const parentContent = document.getElementById('parent_accordion_content');
                            const parentArrow = document.getElementById('parent_accordion_arrow');
                            if (parentContent && parentContent.classList.contains('visible')) {
                                parentContent.classList.remove('visible');
                                if (parentArrow) parentArrow.textContent = '▼';
                            }
                            
                            // Set all checkboxes to their default values
                            const defaultSettings = {
                                'check_style': true,
                                'check_linter': true,
                                'check_security': true,
                                'check_unused': true,
                                'check_best_practices': true,
                                'check_docstrings': true,
                                'check_complexity': false,
                                'check_mypy': false
                            };
                            
                            // Apply default settings
                            Object.keys(defaultSettings).forEach(key => {
                                const checkbox = document.getElementById(key);
                                if (checkbox) {
                                    checkbox.checked = defaultSettings[key];
                                }
                            });
                        } else {
                            // Enable the advanced config section when not using recommended settings
                            parentAccordion.style.opacity = '1';
                            parentAccordion.style.pointerEvents = 'auto';
                        }
                    }
                };
                
                // Set initial state
                updateCustomChecksVisibility();
                
                // Listen for changes
                recommendedCheckbox.addEventListener('change', updateCustomChecksVisibility);
            }
            
            // Drag and drop handling
            const dropZone = document.getElementById('drop-zone');
            
            dropZone.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.style.borderColor = '#8b5cf6';
            });
            
            dropZone.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.style.borderColor = 'rgba(75, 85, 99, 0.7)';
            });
            
            dropZone.addEventListener('drop', function(e) {
                e.preventDefault();
                
                if (e.dataTransfer.files.length > 0) {
                    const fileInput = document.getElementById('file-upload');
                    fileInput.files = e.dataTransfer.files;
                    
                    // Trigger the change event manually
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);
                }
            });
            
            // Save preferences to localStorage
            document.querySelector('form').addEventListener('submit', function() {
                const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                const preferences = {};
                
                checkboxes.forEach(cb => {
                    preferences[cb.name] = cb.checked;
                });
                
                localStorage.setItem('cellsensei_preferences', JSON.stringify(preferences));
            });
            
            // Load preferences if available
            window.addEventListener('load', function() {
                const savedPrefs = localStorage.getItem('cellsensei_preferences');
                if (savedPrefs) {
                    const preferences = JSON.parse(savedPrefs);
                    
                    // Set checkboxes
                    Object.keys(preferences).forEach(key => {
                        const checkbox = document.querySelector(`input[name="${key}"]`);
                        if (checkbox) {
                            checkbox.checked = preferences[key];
                        }
                    });
                }
                
                // Handle function testing UI
                const runFunctionTestsCheckbox = document.getElementById('run_function_tests');
                const testConfigSelect = document.getElementById('test_config');
                
                if (runFunctionTestsCheckbox && testConfigSelect) {
                    // Toggle the test config select based on the checkbox
                    runFunctionTestsCheckbox.addEventListener('change', function() {
                        testConfigSelect.disabled = !this.checked;
                    });
                    
                    // File upload change event to extract functions
                    document.getElementById('file-upload').addEventListener('change', function() {
                        if (this.files.length > 0 && runFunctionTestsCheckbox.checked) {
                            // Indicate that functions will be detected after upload
                            const functionContent = document.getElementById('function_test_content');
                            // Check if the notification is already there
                            if (functionContent && !document.getElementById('function_detection_notice')) {
                                const functionInfo = document.createElement('div');
                                functionInfo.id = 'function_detection_notice';
                                functionInfo.innerHTML = '<p style="color: #8b5cf6; margin-top: 0.5rem; font-weight: 500;">✨ Functions will be detected when you submit the form.</p>';
                                functionContent.appendChild(functionInfo);
                            }
                        }
                    });
                }
            });
        """)
        
        results_div = Div(id="results_div") # Placeholder for results
        
        # Page header with logo
        header = Div(
            Div(
                Div(
                    "🧠",
                    cls="logo"
                ),
                cls="logo-container"
            ),
            Div(
                "CellSensei - Python Code Analyzer",
                cls="title"
            ),
            cls="header"
        )
        
        # Main container
        container = Div(
            header,
            upload_form,
            results_div,
            cls="container"
        )
        
        return Titled("CellSensei - Python Code Analyzer",
            css,
            container,
            script
        )

    @app.route("/upload", methods=["POST"])
    async def handle_upload(req: Request):
        form_data = await req.form()
        notebook_file: UploadFile = form_data.get("notebook_file")

        if not notebook_file or not notebook_file.filename:
            return Titled("Upload Error", P("No file selected or file has no name.")) # Or an HTMX partial response

        # Check for valid file types
        if not (notebook_file.filename.endswith(".ipynb") or notebook_file.filename.endswith(".py")):
            return Titled("Upload Error", P("Invalid file type. Please upload a .ipynb or .py file."))
        
        # Determine file type
        is_notebook = notebook_file.filename.endswith(".ipynb")

        # Extract configuration options
        check_options = {
            "style": form_data.get("check_style") == "on",
            "security": form_data.get("check_security") == "on",
            "linter": form_data.get("check_linter") == "on",
            "docstrings": form_data.get("check_docstrings") == "on",
            "complexity": form_data.get("check_complexity") == "on",
            "mypy": form_data.get("check_mypy") == "on",
            "best_practices": form_data.get("check_best_practices") == "on",
            "unused": form_data.get("check_unused") == "on"
        }
        
        # Get difficulty level
        difficulty = form_data.get("difficulty", "beginner")

        # For security, generate a unique filename to prevent path traversal and name clashes
        import uuid
        temp_file_path = UPLOAD_DIR / f"{uuid.uuid4()}.ipynb"

        try:
            contents = await notebook_file.read()
            with open(temp_file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            return Titled("Upload Error", P(f"Error saving file: {e}"))
        finally:
            await notebook_file.close()
        
        # --- MILESTONE 1: Static Analysis with Configuration ---
        try:
            from sensei_core.static_analyzer import run_static_analysis_on_notebook
            
            # Extract functions from the file
            extracted_functions = extract_functions_from_file(temp_file_path)
            
            # Get available test configurations
            available_configs = get_available_configs()
            
            # Check if function testing was requested
            run_function_tests = form_data.get("run_function_tests") == "on"
            
            # Get the selected configuration if any
            selected_config_path = form_data.get("test_config")
            selected_config = None
            test_results = {}
            
            if run_function_tests and selected_config_path:
                # Find the selected configuration
                for config in available_configs:
                    if config.get("file_path") == selected_config_path:
                        selected_config = config
                        break
                
                # If a config was selected, run the tests
                if selected_config:
                    # Check which functions to test
                    functions_to_test = {}
                    for func_name in extracted_functions:
                        # Check if the function was selected for testing
                        if form_data.get(f"test_function_{func_name}") == "on":
                            functions_to_test[func_name] = extracted_functions[func_name]
                    
                    # Run the tests
                    if functions_to_test:
                        test_results = test_extracted_functions(functions_to_test, selected_config)
            
            # Pass check options to the analyzer
            analysis_results = run_static_analysis_on_notebook(
                notebook_file_path=temp_file_path, 
                options=check_options,
                difficulty=difficulty
            )
            
            # Create a stylish results page based on the mockup
            # Group issues by category
            issue_categories = {
                "security_checks": {"name": "Security Checks", "icon": "🛡️", "color": "red", "messages": []},
                "style_checks": {"name": "Style Checks", "icon": "💻", "color": "yellow", "messages": []},
                "function_checks": {"name": "Function Checks", "icon": "💻", "color": "blue", "messages": []},
                "linter_feedback": {"name": "Linter Feedback", "icon": "⚠️", "color": "orange", "messages": []},
                "unused_variables": {"name": "Unused Variables", "icon": "💻", "color": "purple", "messages": []},
                "type_checking": {"name": "Type Checking", "icon": "✓", "color": "green", "messages": []},
                "best_practices": {"name": "Best Practices", "icon": "✨", "color": "indigo", "messages": []},
                "complexity_checks": {"name": "Complexity Checks", "icon": "🔄", "color": "teal", "messages": []}
            }
            
            # Map the results to our categories
            issue_count = 0
            
            for check_type, messages in analysis_results.items():
                # Skip placeholders like "No issues found"
                real_issues = [msg for msg in messages if not msg.startswith("No ") and not "not yet implemented" in msg]
                
                if check_type in issue_categories:
                    issue_categories[check_type]["messages"] = messages
                    issue_categories[check_type]["count"] = len(real_issues)
                    issue_count += len(real_issues)
                else:
                    # For any other category not explicitly mapped
                    issue_categories[check_type] = {
                        "name": check_type.replace("_", " ").title(),
                        "icon": "📝",
                        "color": "gray",
                        "messages": messages,
                        "count": len(real_issues)
                    }
                    issue_count += len(real_issues)
            
            # Clean up the temporary file after analysis
            try:
                import os
                os.remove(temp_file_path) 
            except:
                print(f"Warning: Could not remove temporary file {temp_file_path}")
            
            # Custom CSS styling for the results page
            css = Style("""
                body {
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    min-height: 100vh;
                    background: linear-gradient(to bottom right, #1a1a2e, #16213e);
                    color: #f0f0f0;
                    padding: 1.5rem;
                    margin: 0;
                }
                
                .container {
                    max-width: 1000px;
                    margin: 0 auto;
                }
                
                .header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 2rem;
                }
                
                .logo-container {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }
                
                .logo-bg {
                    background-color: rgba(236, 72, 153, 0.2);
                    padding: 0.5rem;
                    border-radius: 0.5rem;
                }
                
                .logo {
                    width: 2rem;
                    height: 2rem;
                    background: linear-gradient(to right, #ec4899, #8b5cf6);
                    border-radius: 0.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 1.25rem;
                }
                
                .title {
                    font-size: 1.5rem;
                    font-weight: bold;
                    background: linear-gradient(to right, #a78bfa, #ec4899);
                    -webkit-background-clip: text;
                    background-clip: text;
                    color: transparent;
                }
                
                .button-group {
                    display: flex;
                    gap: 0.75rem;
                }
                
                .btn {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.5rem 1rem;
                    border-radius: 0.5rem;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.3s;
                    border: none;
                    font-size: 0.875rem;
                }
                
                .btn-outline {
                    border: 1px solid #4b5563;
                    background-color: transparent;
                    color: #d1d5db;
                }
                
                .btn-outline:hover {
                    background-color: rgba(75, 85, 99, 0.2);
                }
                
                .btn-primary {
                    background: linear-gradient(to right, #8b5cf6, #6366f1);
                    color: white;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                }
                
                .btn-primary:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                }
                
                .card {
                    background-color: rgba(31, 41, 55, 0.5);
                    backdrop-filter: blur(4px);
                    border-radius: 0.75rem;
                    padding: 1.5rem;
                    border: 1px solid rgba(75, 85, 99, 0.5);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    margin-bottom: 1.5rem;
                }
                
                .summary-title {
                    font-size: 1.25rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: #f0f0f0;
                }
                
                .severity-badge {
                    display: inline-flex;
                    align-items: center;
                    padding: 0.25rem 0.5rem;
                    border-radius: 9999px;
                    font-size: 0.75rem;
                    font-weight: 500;
                }
                
                .severity-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 1rem;
                }
                
                .severity-low {
                    background-color: #10b981;
                    color: white;
                }
                
                .severity-medium {
                    background-color: #f59e0b;
                    color: white;
                }
                
                .severity-high {
                    background-color: #ef4444;
                    color: white;
                }
                
                .issue-count {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    font-size: 1.125rem;
                    margin-bottom: 1rem;
                }
                
                .issue-icon {
                    color: #f59e0b;
                }
                
                .category-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 0.75rem;
                    margin-bottom: 1.5rem;
                }
                
                .category-item {
                    background-color: rgba(31, 41, 55, 0.7);
                    border-radius: 0.5rem;
                    padding: 0.75rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                
                .category-item:hover {
                    background-color: rgba(55, 65, 81, 0.7);
                }
                
                .category-info {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .category-icon {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 1.5rem;
                    height: 1.5rem;
                    background-color: rgba(31, 41, 55, 0.7);
                    border-radius: 0.25rem;
                }
                
                .category-badge {
                    background-color: rgba(31, 41, 55, 0.7);
                    border-radius: 9999px;
                    min-width: 1.5rem;
                    height: 1.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.75rem;
                }
                
                .section-title {
                    font-size: 1.25rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: #f0f0f0;
                }
                
                .collapsible {
                    margin-bottom: 1rem;
                }
                
                .collapsible-header {
                    background-color: rgba(31, 41, 55, 0.5);
                    backdrop-filter: blur(4px);
                    border-radius: 0.5rem;
                    padding: 1rem;
                    border: 1px solid rgba(75, 85, 99, 0.5);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                
                .collapsible-header:hover {
                    background-color: rgba(55, 65, 81, 0.5);
                }
                
                .collapsible-title {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    font-weight: 500;
                }
                
                .collapsible-badge {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .collapsible-content {
                    background-color: rgba(31, 41, 55, 0.3);
                    border: 1px solid rgba(75, 85, 99, 0.5);
                    border-top: none;
                    border-bottom-left-radius: 0.5rem;
                    border-bottom-right-radius: 0.5rem;
                    padding: 1rem;
                    margin-top: -1px;
                }
                
                .collapsible-content.hidden {
                    display: none;
                }
                
                .issue-list {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                
                .issue-item {
                    padding: 0.5rem 0;
                    padding-left: 1rem;
                    border-left-width: 2px;
                    border-left-style: solid;
                    margin-bottom: 0.5rem;
                    font-size: 0.875rem;
                }
                
                .issue-item-red {
                    border-left-color: #ef4444;
                    color: #fca5a5;
                }
                
                .issue-item-yellow {
                    border-left-color: #f59e0b;
                    color: #fcd34d;
                }
                
                .issue-item-blue {
                    border-left-color: #3b82f6;
                    color: #93c5fd;
                }
                
                .issue-item-green {
                    border-left-color: #10b981;
                    color: #6ee7b7;
                }
                
                .issue-item-purple {
                    border-left-color: #8b5cf6;
                    color: #c4b5fd;
                }
                
                .issue-item-orange {
                    border-left-color: #f97316;
                    color: #fdba74;
                }
                
                .issue-item-indigo {
                    border-left-color: #6366f1;
                    color: #a5b4fc;
                }
                
                .issue-item-teal {
                    border-left-color: #14b8a6;
                    color: #5eead4;
                }
                
                .issue-item-gray {
                    border-left-color: #6b7280;
                    color: #d1d5db;
                }
                
                .code-block {
                    background-color: rgba(17, 24, 39, 0.8);
                    padding: 0.75rem;
                    border-radius: 0.5rem;
                    font-family: monospace;
                    font-size: 0.75rem;
                    color: #d1d5db;
                    white-space: pre;
                    overflow-x: auto;
                }
                
                .hidden {
                    display: none;
                }
            """)
            
            # Generate full report for download
            full_report = "# Static Analysis Report\n\n"
            for category_key, category in issue_categories.items():
                if "count" in category and category["count"] > 0:
                    full_report += f"## {category['name']} ({category['count']} issues)\n\n"
                    for msg in category["messages"]:
                        if not msg.startswith("No ") and not "not yet implemented" in msg:
                            full_report += f"- {msg}\n"
                    full_report += "\n"
            
            # Add hidden textarea with report content for download
            report_data = Textarea(
                full_report,
                id="report_data",
                style="display:none;"
            )
            
            # Determine severity based on issue count
            severity = "low"
            severity_text = "Low"
            
            if issue_count > 50:
                severity = "high"
                severity_text = "High"
            elif issue_count > 20:
                severity = "medium"
                severity_text = "Medium"
                
            # Header with navigation buttons
            header = Div(
                Div(
                    Div(
                        Div(
                            "📄",
                            cls="logo"
                        ),
                        cls="logo-bg"
                    ),
                    Div(
                        "Analysis Results",
                        cls="title"
                    ),
                    cls="logo-container"
                ),
                Div(
                    Button(
                        Span("←", style="margin-right: 0.25rem;"),
                        "Back to Home",
                        cls="btn btn-outline",
                        onclick="window.location.href='/'",
                        type="button"
                    ),
                    Button(
                        Span("⬇️", style="margin-right: 0.25rem;"),
                        "Download Report",
                        id="download_report",
                        cls="btn btn-primary",
                        type="button"
                    ),
                    cls="button-group"
                ),
                cls="header"
            )
            
            # Summary card
            summary_card = Div(
                Div(
                    Div(
                        "Summary",
                        cls="summary-title"
                    ),
                    Div(
                        Span("Severity:", style="font-size: 0.875rem; color: #9ca3af;"),
                        Span(
                            severity_text,
                            cls=f"severity-badge severity-{severity}"
                        ),
                        cls="flex items-center gap-2"
                    ),
                    cls="severity-header"
                ),
                Div(
                    Span("⚠️", cls="issue-icon"),
                    f"Found {issue_count} issues in your {notebook_file.filename}",
                    cls="issue-count"
                ),
                Div(
                    H3("Issues by Category:", style="font-size: 1rem; font-weight: 500; color: #d1d5db; margin-bottom: 0.75rem;"),
                    # Create a grid of categories
                    Div(
                        *[
                            Div(
                                Div(
                                    Span(category["icon"], cls="category-icon"),
                                    Span(category["name"], style="font-size: 0.875rem;"),
                                    cls="category-info"
                                ),
                                Div(
                                    category.get("count", 0),
                                    cls="category-badge"
                                ),
                                cls="category-item",
                                onclick=f"document.getElementById('section_{key}').scrollIntoView({{behavior: 'smooth'}})"
                            )
                            for key, category in issue_categories.items()
                            if "count" in category and category["count"] > 0
                        ],
                        cls="category-grid"
                    ),
                ),
                cls="card"
            )
            
            # Detailed analysis sections
            detailed_sections = []
            
            # Create collapsible sections for each category with issues
            for key, category in issue_categories.items():
                if "count" in category and category["count"] > 0:
                    # Create a unique ID for the section
                    section_id = f"section_{key}"
                    content_id = f"content_{key}"
                    
                    # Create issues list based on the category
                    issue_items = []
                    
                    # Special handling for linter feedback to show as code block
                    if key == "linter_feedback" and len(category["messages"]) > 0:
                        # Format linter output as code block
                        issue_items.append(
                            Div(
                                "\n".join(category["messages"]),
                                cls="code-block"
                            )
                        )
                    else:
                        # Regular list of issues
                        for msg in category["messages"]:
                            if not msg.startswith("No ") and not "not yet implemented" in msg:
                                issue_items.append(
                                    Li(
                                        msg,
                                        cls=f"issue-item issue-item-{category['color']}"
                                    )
                                )
                    
                    # Create the collapsible section
                    section = Div(
                        Div(
                            Div(
                                Span(category["icon"], style="color: #8b5cf6;"),
                                category["name"],
                                cls="collapsible-title"
                            ),
                            Div(
                                f"{category['count']} issues",
                                Span("▼", id=f"arrow_{key}"),
                                cls="collapsible-badge"
                            ),
                            cls="collapsible-header",
                            id=section_id,
                            onclick=f"""
                                document.getElementById('{content_id}').classList.toggle('hidden');
                                document.getElementById('arrow_{key}').textContent = 
                                    document.getElementById('arrow_{key}').textContent === '▼' ? '▲' : '▼';
                            """
                        ),
                        Div(
                            *issue_items if issue_items else [P("No specific issues found.")],
                            id=content_id,
                            cls="collapsible-content"
                        ),
                        cls="collapsible"
                    )
                    
                    detailed_sections.append(section)
            
            # Detailed analysis card
            detailed_card = Div(
                H2("Detailed Analysis", cls="section-title"),
                *detailed_sections,
                cls="card"
            ) if detailed_sections else ""
            
            # Add script for download functionality
            download_script = Script("""
                document.getElementById('download_report').addEventListener('click', function() {
                    const reportContent = document.getElementById('report_data').value;
                    const blob = new Blob([reportContent], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'python_analysis_report.txt';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
                
                // Initialize with all sections collapsed
                document.addEventListener('DOMContentLoaded', function() {
                    const collapsibleContents = document.querySelectorAll('.collapsible-content');
                    collapsibleContents.forEach(content => {
                        content.classList.add('hidden');
                    });
                });
            """)
            
            # Function test results section (if any)
            function_test_card = ""
            if test_results:
                function_sections = []
                
                # Calculate total score and max score
                total_score = 0
                max_score = 0
                
                for func_name, func_results in test_results.items():
                    # Count passed tests and calculate score
                    passed_tests = sum(1 for r in func_results if r.get("passed", False))
                    total_tests = len(func_results)
                    
                    # Calculate points
                    func_score = sum(r.get("points", 0) for r in func_results if r.get("passed", False))
                    func_max_score = sum(r.get("points", 0) for r in func_results)
                    
                    total_score += func_score
                    max_score += func_max_score
                    
                    # Create test result items
                    test_items = []
                    for test_result in func_results:
                        test_id = test_result.get("test_id", "unknown")
                        description = test_result.get("description", "")
                        passed = test_result.get("passed", False)
                        error = test_result.get("error")
                        points = test_result.get("points", 0)
                        
                        # Create test status icon
                        status_icon = "✅" if passed else "❌"
                        status_class = "text-green-400" if passed else "text-red-400"
                        
                        # Create test result item
                        test_item = Div(
                            Div(
                                Span(status_icon, style=f"color: {status_class};"),
                                Span(description or test_id, style="margin-left: 0.5rem;"),
                                cls="flex items-center"
                            ),
                            Div(
                                f"{points if passed else 0}/{points} points",
                                style="font-size: 0.75rem; color: #9ca3af;"
                            ),
                            *([Div(
                                f"Error: {error}",
                                style="font-size: 0.75rem; color: #ef4444; margin-top: 0.25rem;"
                            )] if error else []),
                            style="padding: 0.5rem; border-bottom: 1px solid rgba(75, 85, 99, 0.3);"
                        )
                        test_items.append(test_item)
                    
                    # Create function result section
                    function_section = Div(
                        Div(
                            Div(
                                Span("🔍", style="color: #8b5cf6;"),
                                func_name,
                                cls="collapsible-title"
                            ),
                            Div(
                                f"{passed_tests}/{total_tests} tests passed | {func_score}/{func_max_score} points",
                                Span("▼", id=f"func_arrow_{func_name}"),
                                cls="collapsible-badge"
                            ),
                            cls="collapsible-header",
                            id=f"function_section_{func_name}",
                            onclick=f"""
                                document.getElementById('function_content_{func_name}').classList.toggle('hidden');
                                document.getElementById('func_arrow_{func_name}').textContent = 
                                    document.getElementById('func_arrow_{func_name}').textContent === '▼' ? '▲' : '▼';
                            """
                        ),
                        Div(
                            *test_items,
                            id=f"function_content_{func_name}",
                            cls="collapsible-content"
                        ),
                        cls="collapsible"
                    )
                    
                    function_sections.append(function_section)
                
                # Create the function test card
                function_test_card = Div(
                    Div(
                        "Function Tests",
                        style="font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #f0f0f0;"
                    ),
                    Div(
                        Div(
                            "Overall Score:",
                            style="font-weight: 500; color: #d1d5db;"
                        ),
                        Div(
                            f"{total_score}/{max_score} points ({int(total_score/max_score*100) if max_score else 0}%)",
                            style="font-size: 1.25rem; font-weight: 600; color: #a78bfa;"
                        ),
                        style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(75, 85, 99, 0.5);"
                    ),
                    *function_sections,
                    cls="card"
                )
            
            # Main container
            container = Div(
                header,
                summary_card,
                detailed_card,
                function_test_card if test_results else "",
                report_data,
                cls="container"
            )
            
            # Combine all elements
            return Titled("CellSensei - Analysis Results", 
                css,
                container,
                download_script
            )

        except Exception as e:
            # Log the full error on the server
            print(f"Error during static analysis: {e}") # Replace with proper logging
            # import traceback; traceback.print_exc(); # For detailed debugging
            return Titled("Processing Error", P(f"An error occurred during analysis: {e}"))
