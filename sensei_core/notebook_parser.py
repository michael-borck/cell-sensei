import nbformat
import ast
import re
import os
import inspect
import importlib.util
import sys
import yaml
import types
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable, Union

def extract_code_from_notebook(notebook_path) -> Optional[str]:
    """
    Extract all Python code from a Jupyter notebook.
    
    Args:
        notebook_path: Path to the notebook file (str or Path object)
        
    Returns:
        A string containing all code cells joined with newlines, or None if extraction fails
    """
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

def extract_functions_from_code(code_string: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract Python function definitions from code string.
    
    Args:
        code_string: Python code as a string
        
    Returns:
        Dictionary mapping function names to their details (args, body, etc.)
    """
    functions = {}
    
    try:
        tree = ast.parse(code_string)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function name
                func_name = node.name
                
                # Get function arguments
                args = []
                defaults = []
                
                # Process arguments
                for arg in node.args.args:
                    args.append(arg.arg)
                
                # Process default values for arguments
                if node.args.defaults:
                    num_defaults = len(node.args.defaults)
                    num_args = len(node.args.args)
                    defaults = [None] * (num_args - num_defaults) + [ast.unparse(default) for default in node.args.defaults]
                else:
                    defaults = [None] * len(args)
                
                # Get function body as source code
                func_body_lines = code_string.splitlines()[node.lineno-1:node.end_lineno]
                func_body = "\n".join(func_body_lines)
                
                # Get function source code
                func_source = ast.unparse(node)
                
                # Store function details
                functions[func_name] = {
                    "name": func_name,
                    "args": args,
                    "defaults": defaults,
                    "line_number": node.lineno,
                    "body": func_body,
                    "source": func_source,
                    "docstring": ast.get_docstring(node)
                }
    except SyntaxError as e:
        print(f"Syntax error in student code: {e}")
    except Exception as e:
        print(f"Error during function extraction: {e}")
    
    return functions

def extract_functions_from_notebook(notebook_path) -> Dict[str, Dict[str, Any]]:
    """
    Extract all function definitions from a Jupyter notebook.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        Dictionary mapping function names to their details
    """
    code = extract_code_from_notebook(notebook_path)
    if code is None:
        return {}
    
    return extract_functions_from_code(code)

def extract_functions_from_file(file_path) -> Dict[str, Dict[str, Any]]:
    """
    Extract all function definitions from a Python file or notebook.
    
    Args:
        file_path: Path to the file (str or Path object)
        
    Returns:
        Dictionary mapping function names to their details
    """
    file_path_str = str(file_path)
    
    if file_path_str.endswith('.ipynb'):
        return extract_functions_from_notebook(file_path)
    elif file_path_str.endswith('.py'):
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        return extract_functions_from_code(code)
    else:
        print(f"Unsupported file type: {file_path}")
        return {}

def compile_function(function_source: str, function_name: str) -> Optional[Callable]:
    """
    Compile a function from its source code and return the callable.
    
    Args:
        function_source: Source code of the function
        function_name: Name of the function
        
    Returns:
        Callable function object or None if compilation fails
    """
    try:
        # Create a module-like namespace
        namespace = {}
        
        # Compile and execute the function code in the namespace
        exec(function_source, namespace)
        
        # Return the function from the namespace
        return namespace.get(function_name)
    except Exception as e:
        print(f"Error compiling function {function_name}: {e}")
        return None

def load_test_config(config_path: str) -> Dict[str, Any]:
    """
    Load a test configuration file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Dictionary containing the test configuration
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading test configuration {config_path}: {e}")
        return {}

def get_available_configs() -> List[Dict[str, Any]]:
    """
    Get all available test configurations from the assignment_defs directory.
    
    Returns:
        List of loaded configuration objects
    """
    configs = []
    assignment_dir = Path(__file__).parent.parent / "assignment_defs"
    
    if not assignment_dir.exists():
        return configs
    
    for file in assignment_dir.glob("*.yaml"):
        config = load_test_config(str(file))
        if config:
            # Add the file path to the config
            config["file_path"] = str(file)
            configs.append(config)
    
    return configs

def run_function_test(function: Callable, test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a test case on a function and return the result.
    
    Args:
        function: The callable function to test
        test_case: Dictionary containing test case details
        
    Returns:
        Dictionary with test results
    """
    result = {
        "test_id": test_case.get("test_id", "unknown"),
        "description": test_case.get("description", ""),
        "passed": False,
        "points": test_case.get("points", 0),
        "error": None,
        "actual": None
    }
    
    try:
        # Get the inputs
        inputs = test_case.get("inputs", [])
        expected = test_case.get("expected")
        
        # Convert inputs to the right format
        if isinstance(inputs, list):
            actual = function(*inputs)
        else:
            actual = function(inputs)
        
        result["actual"] = actual
        
        # Compare with expected result
        if isinstance(expected, bool):
            # Special handling for boolean comparisons
            result["passed"] = bool(actual) == expected
        elif isinstance(actual, float) and isinstance(expected, (int, float)):
            # Special handling for floating point comparisons
            import math
            result["passed"] = math.isclose(actual, expected, rel_tol=1e-9)
        else:
            # Standard equality check
            result["passed"] = actual == expected
            
    except Exception as e:
        result["error"] = str(e)
    
    return result

def run_pytest_tests(function: Callable, pytest_file: str, function_name: str) -> List[Dict[str, Any]]:
    """
    Run pytest tests for a function.
    
    Args:
        function: The callable function to test
        pytest_file: Path to the pytest file
        function_name: Name of the function
        
    Returns:
        List of test results
    """
    import pytest
    from _pytest.runner import runtestprotocol
    
    results = []
    
    try:
        # Create a temporary module with the function
        module_name = f"student_module_{function_name}"
        module = types.ModuleType(module_name)
        setattr(module, function_name, function)
        sys.modules[module_name] = module
        
        # Also set the function in the global namespace for the pytest file
        globals()[function_name] = function
        
        # Run the pytest file
        pytest_path = Path(__file__).parent.parent / "assignment_defs" / pytest_file
        
        if not pytest_path.exists():
            return [{"test_id": "pytest_error", "description": f"Pytest file {pytest_file} not found", "passed": False}]
        
        # Import the pytest file
        spec = importlib.util.spec_from_file_location("test_module", pytest_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # Run the tests
        for name, obj in inspect.getmembers(test_module):
            if name.startswith("test_") and inspect.isfunction(obj):
                # Create a test result
                test_result = {
                    "test_id": name,
                    "description": obj.__doc__ or name,
                    "passed": False,
                    "error": None
                }
                
                try:
                    # Run the test
                    obj()
                    test_result["passed"] = True
                except Exception as e:
                    test_result["error"] = str(e)
                
                results.append(test_result)
        
    except Exception as e:
        results.append({
            "test_id": "pytest_setup_error",
            "description": "Error setting up pytest",
            "passed": False,
            "error": str(e)
        })
    
    # Clean up
    if module_name in sys.modules:
        del sys.modules[module_name]
    if function_name in globals():
        del globals()[function_name]
    
    return results

def test_extracted_functions(
    functions: Dict[str, Dict[str, Any]], 
    config: Dict[str, Any]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Test extracted functions against test cases defined in a configuration.
    
    Args:
        functions: Dictionary of extracted functions
        config: Test configuration
        
    Returns:
        Dictionary mapping function names to test results
    """
    results = {}
    
    # Get configuration settings
    config_functions = config.get("functions", [])
    
    for func_config in config_functions:
        func_name = func_config.get("name")
        
        if func_name not in functions:
            # Skip functions not found in the student's code
            continue
        
        func_info = functions[func_name]
        func_source = func_info.get("source")
        
        # Compile the function
        function = compile_function(func_source, func_name)
        
        if function is None:
            # Skip if function compilation failed
            results[func_name] = [{
                "test_id": "compilation_error",
                "description": "Function could not be compiled",
                "passed": False,
                "error": "Compilation error"
            }]
            continue
        
        # Run basic tests defined in the config
        function_results = []
        
        for test_case in func_config.get("tests", []):
            test_result = run_function_test(function, test_case)
            function_results.append(test_result)
        
        # Run pytest tests if specified
        pytest_file = func_config.get("pytest_file")
        if pytest_file:
            pytest_results = run_pytest_tests(function, pytest_file, func_name)
            function_results.extend(pytest_results)
        
        results[func_name] = function_results
    
    return results
