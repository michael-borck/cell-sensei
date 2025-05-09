import nbformat
import ast
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our notebook parser to reuse code
from sensei_core.notebook_parser import extract_code_from_notebook

def get_code_from_file(file_path) -> Optional[str]:
    """
    Extract code from either a Jupyter notebook or Python script.
    
    Args:
        file_path: Path to the file (str or Path object)
        
    Returns:
        String containing the code, or None if extraction fails
    """
    # Convert to string if it's a Path object
    file_path_str = str(file_path)
    
    # Check file extension
    if file_path_str.endswith('.ipynb'):
        # It's a notebook, use the notebook parser
        return extract_code_from_notebook(file_path)
    elif file_path_str.endswith('.py'):
        # It's a Python script, read it directly
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading Python file {file_path}: {e}")
            return None
    else:
        print(f"Unsupported file type: {file_path}")
        return None

def custom_ast_checks(code_string: str) -> List[str]:
    """
    Performs basic AST checks for disallowed imports or functions.
    
    Args:
        code_string: The Python code to analyze
        
    Returns:
        List of issues found in the code
    """
    issues = []
    # Security-related disallowed modules
    disallowed_imports = {
        "os", "subprocess", "shutil", "sys", "socket", "requests", 
        "urllib", "http", "ftplib", "telnetlib", "smtplib"
    }
    # Potentially dangerous built-in functions 
    disallowed_functions = {"eval", "exec", "__import__", "globals", "locals", "compile"}

    try:
        tree = ast.parse(code_string)
        
        # Check for style issues
        for node in ast.walk(tree):
            # Check variable naming style
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id.isupper() and len(target.id) > 1 and not target.id.startswith("_"):
                            issues.append(f"Style: Variable '{target.id}' at line {node.lineno} is all uppercase. This style is typically reserved for constants.")
                        elif target.id.startswith("__") and not target.id.endswith("__"):
                            issues.append(f"Style: Variable '{target.id}' at line {node.lineno} uses double underscore prefix, which is typically reserved for name mangling in classes.")
            
            # Check for security issues
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in disallowed_imports or any(alias.name.startswith(f"{mod}.") for mod in disallowed_imports):
                        issues.append(f"Security: Disallowed import found: '{alias.name}' at line {node.lineno}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module in disallowed_imports or any(node.module.startswith(f"{mod}.") for mod in disallowed_imports)):
                    issues.append(f"Security: Disallowed import from found: '{node.module}' at line {node.lineno}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in disallowed_functions:
                    issues.append(f"Security: Disallowed function call found: '{node.func.id}()' at line {node.lineno}")
                
            # Check for common errors
            if isinstance(node, ast.FunctionDef) and not node.body:
                issues.append(f"Error: Function '{node.name}' at line {node.lineno} has an empty body.")
            
            # Check for unused imports (basic check)
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                # More sophisticated unused import detection would require tracking variable usage
                pass
                
    except SyntaxError as e:
        issues.append(f"Syntax error in student code: {e}")
    except Exception as e:
        issues.append(f"Error during AST check: {str(e)}")
    
    return issues

def style_check_functions(code_string: str) -> List[str]:
    """
    Check for style issues specifically related to function definitions.
    
    Args:
        code_string: The Python code to analyze
        
    Returns:
        List of style issues in function definitions
    """
    issues = []
    
    try:
        tree = ast.parse(code_string)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function name style (should be snake_case)
                if not node.name.islower() and "_" not in node.name and not node.name.startswith("__"):
                    issues.append(f"Style: Function name '{node.name}' at line {node.lineno} should use snake_case naming convention.")
                
                # Check for docstring
                if not ast.get_docstring(node):
                    issues.append(f"Style: Function '{node.name}' at line {node.lineno} is missing a docstring.")
                
                # Check argument names
                for arg in node.args.args:
                    if not arg.arg.islower() and "_" not in arg.arg:
                        issues.append(f"Style: Argument '{arg.arg}' in function '{node.name}' at line {node.lineno} should use snake_case naming convention.")
    
    except SyntaxError as e:
        issues.append(f"Syntax error in student code: {e}")
    except Exception as e:
        issues.append(f"Error during function style check: {str(e)}")
    
    return issues

def run_ruff_linter(code_string: str) -> List[str]:
    """
    Run the Ruff linter on the provided code.
    
    Args:
        code_string: The Python code to analyze
        
    Returns:
        List of linting issues found
    """
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code_string)
        
        # Run Ruff on the temporary file
        ruff_result = subprocess.run(
            ["ruff", "check", temp_file_path], 
            capture_output=True, 
            text=True,
            timeout=10  # Timeout after 10 seconds
        )
        
        # Process the output
        linter_output = []
        if ruff_result.stdout:
            # Process each line to make it more readable
            for line in ruff_result.stdout.splitlines():
                # Remove the temp file path from the output for clarity
                cleaned_line = line.replace(temp_file_path, "student_code.py")
                linter_output.append(cleaned_line)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return linter_output if linter_output else ["No linting issues found."]
    
    except subprocess.TimeoutExpired:
        return ["Linting timed out. Code may be too complex or contain infinite loops."]
    except Exception as e:
        return [f"Error running linter: {str(e)}"]

def check_code_complexity(code_string: str) -> List[str]:
    """
    Check for code complexity issues using AST.
    
    Args:
        code_string: The Python code to analyze
        
    Returns:
        List of complexity issues
    """
    issues = []
    
    try:
        tree = ast.parse(code_string)
        
        for node in ast.walk(tree):
            # Check function complexity by counting branches
            if isinstance(node, ast.FunctionDef):
                # Simple branch counting for if/elif/else, for, while
                branch_count = 0
                
                for subnode in ast.walk(node):
                    if isinstance(subnode, (ast.If, ast.For, ast.While)):
                        branch_count += 1
                
                if branch_count > 10:
                    issues.append(f"Complexity: Function '{node.name}' at line {node.lineno} has high complexity ({branch_count} branches). Consider refactoring.")
                elif branch_count > 5:
                    issues.append(f"Complexity: Function '{node.name}' at line {node.lineno} has moderate complexity ({branch_count} branches). Consider simplifying.")
    
    except SyntaxError as e:
        issues.append(f"Syntax error in student code: {e}")
    except Exception as e:
        issues.append(f"Error during complexity check: {str(e)}")
    
    return issues

def check_best_practices(code_string: str) -> List[str]:
    """
    Check for Python best practices.
    
    Args:
        code_string: The Python code to analyze
        
    Returns:
        List of best practice suggestions
    """
    issues = []
    
    try:
        tree = ast.parse(code_string)
        
        for node in ast.walk(tree):
            # Check for 'is' vs '==' with None, True, False
            if isinstance(node, ast.Compare):
                if isinstance(node.ops[0], (ast.Eq, ast.NotEq)) and len(node.comparators) == 1:
                    if isinstance(node.comparators[0], ast.Constant):
                        if node.comparators[0].value is None:
                            issues.append(f"Best Practice: Use 'is None' instead of '== None' at line {node.lineno}")
                        elif node.comparators[0].value is True:
                            issues.append(f"Best Practice: Use 'is True' instead of '== True' at line {node.lineno}")
                        elif node.comparators[0].value is False:
                            issues.append(f"Best Practice: Use 'is False' instead of '== False' at line {node.lineno}")
            
            # Check for inefficient list/dict building patterns
            if isinstance(node, ast.FunctionDef):
                has_list_append_loop = False
                appended_var = None
                
                # Look for loops with list.append()
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.For):
                        for stmt in subnode.body:
                            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                                if (isinstance(stmt.value.func, ast.Attribute) and 
                                    stmt.value.func.attr == 'append'):
                                    has_list_append_loop = True
                                    appended_var = stmt.value.func.value.id if isinstance(stmt.value.func.value, ast.Name) else None
                
                if has_list_append_loop and appended_var:
                    issues.append(f"Best Practice: Consider using a list comprehension instead of appending in a loop in function '{node.name}' at line {node.lineno}")
    
    except SyntaxError as e:
        issues.append(f"Syntax error in student code: {e}")
    except Exception as e:
        issues.append(f"Error during best practices check: {str(e)}")
    
    return issues

def check_unused_variables(code_string: str) -> List[str]:
    """
    Check for unused variables and imports.
    
    Args:
        code_string: The Python code to analyze
        
    Returns:
        List of unused variable warnings
    """
    issues = []
    
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code_string)
        
        # Run Ruff with the specific rule for unused variables
        ruff_result = subprocess.run(
            ["ruff", "check", "--select=F841", temp_file_path], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        # Process the output
        if ruff_result.stdout:
            for line in ruff_result.stdout.splitlines():
                # Clean up the output
                cleaned_line = line.replace(temp_file_path, "student_code.py")
                issues.append(f"Unused: {cleaned_line}")
        
        # Clean up
        os.unlink(temp_file_path)
    
    except subprocess.TimeoutExpired:
        issues.append("Timeout during unused variable check.")
    except Exception as e:
        issues.append(f"Error checking for unused variables: {str(e)}")
    
    return issues

def run_mypy_check(code_string: str) -> List[str]:
    """
    Run mypy type checking on the code.
    
    Args:
        code_string: The Python code to analyze
        
    Returns:
        List of type checking issues
    """
    issues = []
    
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code_string)
        
        # Run mypy on the temporary file
        mypy_result = subprocess.run(
            ["mypy", "--ignore-missing-imports", temp_file_path], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        # Process the output
        if mypy_result.stdout:
            for line in mypy_result.stdout.splitlines():
                # Clean up the output
                cleaned_line = line.replace(temp_file_path, "student_code.py")
                if "error:" in cleaned_line:
                    issues.append(f"Type: {cleaned_line}")
        
        # Check for errors in stderr as well
        if mypy_result.stderr and "error:" in mypy_result.stderr:
            issues.append(f"Type checking error: {mypy_result.stderr}")
        
        # Clean up
        os.unlink(temp_file_path)
        
        return issues if issues else ["No type checking issues found."]
    
    except FileNotFoundError:
        return ["mypy is not installed or not in PATH. Type checking skipped."]
    except subprocess.TimeoutExpired:
        return ["Type checking timed out."]
    except Exception as e:
        return [f"Error during type checking: {str(e)}"]

def run_static_analysis_on_notebook(notebook_file_path: str, options: Dict[str, bool] = None, difficulty: str = "beginner") -> Dict[str, List[str]]:
    """
    Main function for static analysis in Milestone 1.
    Performs configurable checks based on options and difficulty level.
    
    Args:
        notebook_file_path: Path to the notebook file
        options: Dictionary of check options to enable/disable
        difficulty: Difficulty level (beginner, intermediate, advanced)
        
    Returns:
        Dictionary with results from different types of analysis
    """
    # Default all options to True if not provided
    if options is None:
        options = {
            "style": True,
            "security": True,
            "linter": True,
            "docstrings": True,
            "complexity": False,
            "mypy": False,
            "best_practices": True,
            "unused": True
        }
    
    # Initialize empty results
    results = {}
    
    # Extract code from file (either notebook or Python script)
    code_to_analyze = get_code_from_file(notebook_file_path)
    if code_to_analyze is None:
        return {"error": ["Could not extract code from file."]}
    
    if not code_to_analyze.strip():
        return {"error": ["No Python code found in the file."]}
    
    # Run checks based on enabled options
    
    # Security checks (always run for safety)
    if options.get("security", True):
        ast_issues = [issue for issue in custom_ast_checks(code_to_analyze) 
                     if issue.startswith("Security:")]
        results["security_checks"] = ast_issues if ast_issues else ["No security issues found."]
    
    # Style checks
    if options.get("style", True):
        style_issues = [issue for issue in custom_ast_checks(code_to_analyze) 
                       if issue.startswith("Style:")]
        results["style_checks"] = style_issues if style_issues else ["No style issues found."]
    
    # Function style checks
    if options.get("docstrings", True):
        func_issues = style_check_functions(code_to_analyze)
        results["function_checks"] = func_issues if func_issues else ["No function style issues found."]
    
    # Linter feedback
    if options.get("linter", True):
        linter_results = run_ruff_linter(code_to_analyze)
        results["linter_feedback"] = linter_results
    
    # Complexity checks
    if options.get("complexity", False):
        complexity_issues = check_code_complexity(code_to_analyze)
        results["complexity_checks"] = complexity_issues if complexity_issues else ["No complexity issues found."]
    
    # Best practices
    if options.get("best_practices", True):
        best_practice_issues = check_best_practices(code_to_analyze)
        results["best_practices"] = best_practice_issues if best_practice_issues else ["No best practice issues found."]
    
    # Unused variables
    if options.get("unused", True):
        unused_issues = check_unused_variables(code_to_analyze)
        results["unused_variables"] = unused_issues if unused_issues else ["No unused variables found."]
    
    # Type checking (mypy)
    if options.get("mypy", False):
        # Only run mypy if explicitly enabled - it might not be installed
        mypy_issues = run_mypy_check(code_to_analyze)
        results["type_checking"] = mypy_issues
    
    # Adjust output based on difficulty level
    if difficulty == "beginner":
        # Simplify messages for beginners
        for check_type, messages in results.items():
            simplified_messages = []
            for msg in messages:
                # Make messages more beginner-friendly
                if check_type == "linter_feedback" and ":" in msg:
                    # Simplify linter messages
                    parts = msg.split(":", 3)
                    if len(parts) >= 4:
                        simplified_messages.append(f"Line {parts[1]}: {parts[3].strip()}")
                    else:
                        simplified_messages.append(msg)
                else:
                    simplified_messages.append(msg)
            results[check_type] = simplified_messages
    
    return results

