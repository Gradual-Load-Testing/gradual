"""
The plugin_loader module provides functionality to load custom request functions
from Python files and convert them into RequestConfig objects for stress testing.

This module handles:
1. Importing Python files containing decorated request functions
2. Discovering functions decorated with @request
3. Creating RequestConfig objects from these functions
4. Managing completion callbacks for request functions
"""

import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional

from gradual.configs.request import RequestConfig
from gradual.constants.request_types import RequestType


class PluginLoader:
    """
    Loader for custom request functions from Python files.

    This class handles the discovery and loading of request functions that are
    decorated with @request and their associated completion callbacks.
    """

    def __init__(self):
        self._request_functions: Dict[str, Callable] = {}
        self._completion_callbacks: Dict[str, Callable] = {}
        self._loaded_modules: Dict[str, Any] = {}

    def load_plugin_file(self, filepath: str) -> List[RequestConfig]:
        """
        Load a Python file and extract RequestConfig objects from decorated functions.

        Args:
            file_path (str): Path to the Python file containing request functions

        Returns:
            List[RequestConfig]: List of RequestConfig objects created from decorated functions

        Raises:
            FileNotFoundError: If the specified file doesn't exist
            ImportError: If there's an error importing the module
        """
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(f"Plugin file not found: {file_path}")

        # Load the module
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Store the loaded module
        self._loaded_modules[module_name] = module

        # Discover request functions and completion callbacks
        self._discover_functions(module)

        # Create RequestConfig objects
        return self._create_request_configs()

    def _discover_functions(self, module: ModuleType) -> None:
        """
        Discover request functions and completion callbacks in a module.

        Args:
            module: The loaded module to inspect
        """
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                # Check if function has request decorator metadata
                if hasattr(obj, "_is_request_function"):
                    self._request_functions[name] = obj

                # Check if function has completion callback metadata
                if hasattr(obj, "_is_completion_callback"):
                    target_function = getattr(obj, "_target_request_function", None)
                    if target_function:
                        self._completion_callbacks[target_function] = obj

    def _create_request_configs(self) -> List[RequestConfig]:
        """
        Create RequestConfig objects from discovered request functions.

        Returns:
            List[RequestConfig]: List of RequestConfig objects
        """
        configs = []

        for func_name, func in self._request_functions.items():
            # Get function metadata
            func_metadata = getattr(func, "_request_metadata", {})

            # Use the name from metadata if provided, otherwise use function name
            request_name = func_metadata.get("name", func_name)

            # Map string type to RequestType enum
            type_str = func_metadata.get("type", None)
            # Will trigger auto-detection in RequestConfig
            request_type = None
            if isinstance(type_str, str):
                if type_str.lower() == "http":
                    request_type = RequestType.http
                elif type_str.lower() == "websocket":
                    request_type = RequestType.websocket
                else:
                    # Default for unknown or "custom"
                    request_type = RequestType.custom

            # Create RequestConfig
            config = RequestConfig(
                name=request_name,
                params=func_metadata.get("params", {}),
                http_method=func_metadata.get("http_method", "get"),
                expected_response_time=func_metadata.get("expected_response_time", 1.0),
                context={
                    "function": func,
                    "completion_callback": self._completion_callbacks.get(request_name),
                    "metadata": func_metadata,
                },
                url=func_metadata.get("url", ""),
                auth=func_metadata.get("auth", None),
                type=request_type,
            )

            configs.append(config)

        return configs

    def get_request_function(self, name: str) -> Optional[Callable]:
        """
        Get a request function by name.

        Args:
            name (str): Name of the request function

        Returns:
            Optional[Callable]: The request function if found, None otherwise
        """
        return self._request_functions.get(name)

    def get_completion_callback(self, request_name: str) -> Optional[Callable]:
        """
        Get a completion callback for a request function.

        Args:
            request_name (str): Name of the request function

        Returns:
            Optional[Callable]: The completion callback if found, None otherwise
        """
        return self._completion_callbacks.get(request_name)

    def clear_state(self):
        """
        Clear the internal state of the plugin loader.

        This method clears all discovered functions and callbacks, useful for
        testing or when loading multiple files that should be independent.
        """
        self._request_functions.clear()
        self._completion_callbacks.clear()
        self._loaded_modules.clear()


# Global plugin loader instance
_plugin_loader = PluginLoader()


def get_plugin_loader() -> PluginLoader:
    """
    Get the global plugin loader instance.

    Returns:
        PluginLoader: The global plugin loader instance
    """
    return _plugin_loader


def load_request_configs_from_file(file_path: str) -> List[RequestConfig]:
    """
    Load RequestConfig objects from a Python file.

    This is a convenience function that uses the global plugin loader
    to load request configurations from a Python file.

    Args:
        file_path (str): Path to the Python file containing request functions

    Returns:
        List[RequestConfig]: List of RequestConfig objects
    """
    # Clear state before loading to ensure clean slate
    _plugin_loader.clear_state()
    return _plugin_loader.load_plugin_file(file_path)
