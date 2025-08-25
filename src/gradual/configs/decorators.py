"""
The decorators module provides decorators for marking functions as request functions
and completion callbacks in the stress testing framework.

This module includes:
1. @request decorator for marking functions as request functions
2. @on_call_completion decorator for marking completion callbacks
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional, cast


def request(
    name: Optional[str] = None,
    url: str = "",
    params: Optional[Dict[str, Any]] = None,
    http_method: str = "get",
    expected_response_time: float = 1.0,
    auth: Optional[str] = None,
    type: Optional[str] = None,
):
    """
    Decorator to mark a function as a request function.

    This decorator marks a function as a request function that can be executed
    during stress testing. The function will be discovered by the plugin loader
    and converted into a RequestConfig object.

    Args:
        name (Optional[str]): Custom name for the request (defaults to function name)
        url (str): Target URL for the request
        params (Optional[Dict[str, Any]]): Parameters to be sent with the request
        http_method (str): HTTP method to use (for HTTP requests)
        expected_response_time (float): Expected response time in seconds
        auth (Optional[str]): Authentication method to use
        type (Optional[str]): Type of request (http, websocket, etc.)

    Returns:
        Callable: Decorated function with request metadata
    """

    def decorator(func: Callable) -> Callable:
        # Store metadata on the function
        cast(Any, func)._is_request_function = True
        cast(Any, func)._request_metadata = {
            "name": name or func.__name__,
            "url": url,
            "params": params or {},
            "http_method": http_method,
            "expected_response_time": expected_response_time,
            "auth": auth,
            "type": type,
        }

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Copy metadata to wrapper
        cast(Any, wrapper)._is_request_function = True
        cast(Any, wrapper)._request_metadata = cast(Any, func)._request_metadata

        return wrapper

    return decorator


def on_call_completion(name: str):
    """
    Decorator to mark a function as a completion callback for a request function.

    This decorator marks a function as a completion callback that will be called
    after a specific request function completes execution.

    Args:
        name (str): Name of the request function this callback is associated with

    Returns:
        Callable: Decorated function with completion callback metadata
    """

    def decorator(func: Callable) -> Callable:
        # Store metadata on the function
        cast(Any, func)._is_completion_callback = True
        cast(Any, func)._target_request_function = name

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Copy metadata to wrapper
        cast(Any, wrapper)._is_completion_callback = True
        cast(Any, wrapper)._target_request_function = name

        return wrapper

    return decorator
