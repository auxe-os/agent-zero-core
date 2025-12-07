import re, os, importlib, importlib.util, inspect
from types import ModuleType
from typing import Any, Type, TypeVar
from .dirty_json import DirtyJson
from .files import get_abs_path, deabsolute_path
import regex
from fnmatch import fnmatch

def json_parse_dirty(json:str) -> dict[str,Any] | None:
    """Parses a dirty JSON string and returns a dictionary.

    Args:
        json: The dirty JSON string to parse.

    Returns:
        A dictionary representation of the JSON object, or None if parsing
        fails.
    """
    if not json or not isinstance(json, str):
        return None

    ext_json = extract_json_object_string(json.strip())
    if ext_json:
        try:
            data = DirtyJson.parse_string(ext_json)
            if isinstance(data,dict): return data
        except Exception:
            # If parsing fails, return None instead of crashing
            return None
    return None

def extract_json_object_string(content):
    """Extracts a JSON object string from a larger string.

    Args:
        content: The string to extract the JSON object from.

    Returns:
        The extracted JSON object string, or an empty string if no object
        is found.
    """
    start = content.find('{')
    if start == -1:
        return ""

    # Find the first '{'
    end = content.rfind('}')
    if end == -1:
        # If there's no closing '}', return from start to the end
        return content[start:]
    else:
        # If there's a closing '}', return the substring from start to end
        return content[start:end+1]

def extract_json_string(content):
    """Extracts a JSON string from a larger string.

    Args:
        content: The string to extract the JSON from.

    Returns:
        The extracted JSON string, or an empty string if no JSON is found.
    """
    # Regular expression pattern to match a JSON object
    pattern = r'\{(?:[^{}]|(?R))*\}|\[(?:[^\[\]]|(?R))*\]|"(?:\\.|[^"\\])*"|true|false|null|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?'

    # Search for the pattern in the content
    match = regex.search(pattern, content)

    if match:
        # Return the matched JSON string
        return match.group(0)
    else:
        return ""

def fix_json_string(json_string):
    """Fixes a JSON string by escaping unescaped line breaks.

    Args:
        json_string: The JSON string to fix.

    Returns:
        The fixed JSON string.
    """
    # Function to replace unescaped line breaks within JSON string values
    def replace_unescaped_newlines(match):
        return match.group(0).replace('\n', '\\n')

    # Use regex to find string values and apply the replacement function
    fixed_string = re.sub(r'(?<=: ")(.*?)(?=")', replace_unescaped_newlines, json_string, flags=re.DOTALL)
    return fixed_string


T = TypeVar('T')  # Define a generic type variable

def import_module(file_path: str) -> ModuleType:
    """Imports a Python module from a file path.

    Args:
        file_path: The path to the Python file.

    Returns:
        The imported module.
    """
    # Handle file paths with periods in the name using importlib.util
    abs_path = get_abs_path(file_path)
    module_name = os.path.basename(abs_path).replace('.py', '')
    
    # Create the module spec and load the module
    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {abs_path}")
        
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_classes_from_folder(folder: str, name_pattern: str, base_class: Type[T], one_per_file: bool = True) -> list[Type[T]]:
    """Loads all classes from a folder that match a given pattern and are a
    subclass of a given base class.

    Args:
        folder: The folder to load classes from.
        name_pattern: A glob pattern to match filenames against.
        base_class: The base class to filter by.
        one_per_file: Whether to load only one class per file.

    Returns:
        A list of the loaded classes.
    """
    classes = []
    abs_folder = get_abs_path(folder)

    # Get all .py files in the folder that match the pattern, sorted alphabetically
    py_files = sorted(
        [file_name for file_name in os.listdir(abs_folder) if fnmatch(file_name, name_pattern) and file_name.endswith(".py")]
    )

    # Iterate through the sorted list of files
    for file_name in py_files:
        file_path = os.path.join(abs_folder, file_name)
        # Use the new import_module function
        module = import_module(file_path)

        # Get all classes in the module
        class_list = inspect.getmembers(module, inspect.isclass)

        # Filter for classes that are subclasses of the given base_class
        # iterate backwards to skip imported superclasses
        for cls in reversed(class_list):
            if cls[1] is not base_class and issubclass(cls[1], base_class):
                classes.append(cls[1])
                if one_per_file:
                    break

    return classes

def load_classes_from_file(file: str, base_class: type[T], one_per_file: bool = True) -> list[type[T]]:
    """Loads all classes from a file that are a subclass of a given base class.

    Args:
        file: The file to load classes from.
        base_class: The base class to filter by.
        one_per_file: Whether to load only one class per file.

    Returns:
        A list of the loaded classes.
    """
    classes = []
    # Use the new import_module function
    module = import_module(file)
    
    # Get all classes in the module
    class_list = inspect.getmembers(module, inspect.isclass)
    
    # Filter for classes that are subclasses of the given base_class
    # iterate backwards to skip imported superclasses
    for cls in reversed(class_list):
        if cls[1] is not base_class and issubclass(cls[1], base_class):
            classes.append(cls[1])
            if one_per_file:
                break
                
    return classes
