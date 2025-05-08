from fasthtml.common import *
from fasthtml.components import Form # Explicit import if not in common needed for this
import nbformat # For reading notebook in M1 for static analysis
from starlette.datastructures import UploadFile
from starlette.requests import Request # For type hinting if needed
from pathlib import Path

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
        # Simple upload form
        upload_form = Form(
            H3("Upload your Jupyter Notebook (.ipynb)"),
            Input(type="file", name="notebook_file", id="notebook_file", accept=".ipynb"),
            Button("Test Notebook", type="submit", cls="secondary"),
            action="/upload", method="post", enctype="multipart/form-data",
            # HTMX attributes for later milestones (displaying results)
            # hx_post="/upload", hx_target="#results_div", hx_swap="innerHTML", hx_encoding="multipart/form-data"
        )
        results_div = Div(id="results_div") # Placeholder for results
        
        return Titled("CellSensei - Notebook Grader",
            P("Welcome to CellSensei! Upload your notebook to get it checked."),
            upload_form,
            results_div
        )

    @app.route("/upload", methods=["POST"])
    async def handle_upload(req: Request):
        form_data = await req.form()
        notebook_file: UploadFile = form_data.get("notebook_file")

        if not notebook_file or not notebook_file.filename:
            return Titled("Upload Error", P("No file selected or file has no name.")) # Or an HTMX partial response

        if not notebook_file.filename.endswith(".ipynb"):
            return Titled("Upload Error", P("Invalid file type. Please upload a .ipynb file."))

        # Save the file temporarily
        # WARNING: In a real app, generate a secure, unique filename
        # and ensure the UPLOAD_DIR is secure and cleaned up.
        temp_file_path = UPLOAD_DIR / notebook_file.filename 
        # Note: student filenames could clash or contain malicious characters.
        # A better approach for temp_file_path is Path(UPLOAD_DIR) / str(uuid.uuid4()) + ".ipynb"

        try:
            contents = await notebook_file.read()
            with open(temp_file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            return Titled("Upload Error", P(f"Error saving file: {e}"))
        finally:
            await notebook_file.close()
        
        # --- MILESTONE 1: Static Analysis ---
        # For now, this will be a simple placeholder.
        # In reality, you'd call your static_analyzer module here.
        try:
            from grading_module.static_analyzer import run_static_analysis_on_notebook
            # This function would read temp_file_path, extract code, run AST/linters
            analysis_results = run_static_analysis_on_notebook(temp_file_path)
            
            # Simple way to display results for Milestone 1 (synchronous)
            # This will be improved with HTMX for Celery later.
            result_items = [H4("Static Analysis Report:")]
            if isinstance(analysis_results, dict):
                for check_type, messages in analysis_results.items():
                    result_items.append(H5(check_type.replace("_", " ").title()))
                    if messages:
                        result_items.append(Ul(*[Li(str(msg)) for msg in messages]))
                    else:
                        result_items.append(P("No issues found."))
            else: # Simple string for now
                result_items.append(P(str(analysis_results)))

            # Clean up the temp file after analysis
            # os.remove(temp_file_path) # Do this after all processing

            return Titled("Analysis Results", *result_items)

        except Exception as e:
            # Log the full error on the server
            print(f"Error during static analysis: {e}") # Replace with proper logging
            # import traceback; traceback.print_exc(); # For detailed debugging
            return Titled("Processing Error", P(f"An error occurred during analysis: {e}"))
