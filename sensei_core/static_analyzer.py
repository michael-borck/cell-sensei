import nbformat
import ast
# For later milestones, you'd import subprocess to call Ruff/Black
# import subprocess 

def extract_code_from_notebook(notebook_path):
    """Extracts all Python code from a notebook file."""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb_content = nbformat.read(f, as_version=4)
        
        all_code = []
        for cell in nb_content.cells:
            if cell.cell_type == 'code':
                all_code.append(cell.source)
        return "\n".join(all_code)
    except Exception as e:
        print(f"Error reading or parsing notebook {notebook_path}: {e}")
        return None

def custom_ast_checks(code_string):
    """Performs basic AST checks for disallowed imports or functions."""
    issues = []
    disallowed_imports = {"os", "subprocess", "shutil", "sys"} # Example
    disallowed_functions = {"eval", "exec"} # Example, note: exec is used by us later carefully

    try:
        tree = ast.parse(code_string)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in disallowed_imports:
                        issues.append(f"Disallowed import found: '{alias.name}' at line {node.lineno}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module in disallowed_imports:
                    issues.append(f"Disallowed import from found: '{node.module}' at line {node.lineno}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in disallowed_functions:
                    issues.append(f"Disallowed function call found: '{node.func.id}()' at line {node.lineno}")
    except SyntaxError as e:
        issues.append(f"Syntax error in student code: {e}")
    except Exception as e:
        issues.append(f"Error during AST check: {str(e)}")
    return issues

def run_static_analysis_on_notebook(notebook_file_path):
    """
    Main function for static analysis in Milestone 1.
    Later, this will also call linters/formatters.
    """
    results = {
        "custom_ast_checks": [],
        "linter_feedback": ["Linter not yet implemented in M1."],
        "formatter_feedback": ["Formatter check not yet implemented in M1."]
    }

    code_to_analyze = extract_code_from_notebook(notebook_file_path)
    if code_to_analyze is None:
        results["custom_ast_checks"].append("Could not extract code from notebook.")
        return results
    
    if not code_to_analyze.strip():
         results["custom_ast_checks"].append("No Python code found in the notebook cells.")
         return results

    ast_issues = custom_ast_checks(code_to_analyze)
    if ast_issues:
        results["custom_ast_checks"].extend(ast_issues)
    else:
        results["custom_ast_checks"].append("No specific issues found with disallowed patterns.")
    
    # Placeholder for where you'd call linters/formatters as subprocesses in later iterations of M1 or M2
    # For example:
    # temp_py_file = "temp_student_code.py"
    # with open(temp_py_file, "w") as f:
    #     f.write(code_to_analyze)
    #
    # ruff_result = subprocess.run(["ruff", "check", temp_py_file], capture_output=True, text=True)
    # if ruff_result.stdout:
    #     results["linter_feedback"] = ruff_result.stdout.splitlines()
    # os.remove(temp_py_file)

    return results

