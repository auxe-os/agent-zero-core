from contextvars import ContextVar
from typing import Any, TypeVar, cast, Optional, Dict

T = TypeVar("T")

# no mutable default — None is safe
_context_data: ContextVar[Optional[Dict[str, Any]]] = ContextVar("_context_data", default=None)


def _ensure_context() -> Dict[str, Any]:
    """Ensures that a context dictionary exists and returns it.

    Returns:
        The context dictionary.
    """
    data = _context_data.get()
    if data is None:
        data = {}
        _context_data.set(data)
    return data


def set_context_data(key: str, value: Any):
    """Sets a key-value pair in the current async/task context.

    Args:
        key: The key to set.
        value: The value to set.
    """
    data = _ensure_context()
    if data.get(key) == value:
        return
    data[key] = value
    _context_data.set(data)


def delete_context_data(key: str):
    """Deletes a key from the current async/task context.

    Args:
        key: The key to delete.
    """
    data = _ensure_context()
    if key in data:
        del data[key]
        _context_data.set(data)


def get_context_data(key: Optional[str] = None, default: T = None) -> T:
    """Gets a value from the current context.

    If a key is provided, returns the value for that key, or the default
    value if the key is not found. If no key is provided, returns the entire
    context dictionary.

    Args:
        key: The key to get.
        default: The default value to return if the key is not found.

    Returns:
        The value for the given key, or the entire context dictionary.
    """
    data = _ensure_context()
    if key is None:
        return cast(T, data)
    return cast(T, data.get(key, default))


def clear_context_data():
    """Clears the entire context dictionary."""
    _context_data.set({})
