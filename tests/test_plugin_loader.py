"""
Tests for the plugin loader and decorator functionality.
"""

import os
import tempfile

import pytest

from gradual.configs.decorators import on_call_completion, request
from gradual.configs.plugin_loader import load_request_configs_from_file
from gradual.configs.request import RequestConfig


def test_request_decorator():
    """Test that the @request decorator properly marks functions."""

    @request(name="test_request", expected_response_time=1.0)
    def test_func():
        return "test"

    assert hasattr(test_func, "_is_request_function")
    assert test_func._is_request_function is True
    assert hasattr(test_func, "_request_metadata")
    assert test_func._request_metadata["name"] == "test_request"
    assert test_func._request_metadata["expected_response_time"] == 1.0


def test_on_call_completion_decorator():
    """Test that the @on_call_completion decorator properly marks functions."""

    @on_call_completion(name="test_request")
    def completion_func():
        return "completed"

    assert hasattr(completion_func, "_is_completion_callback")
    assert completion_func._is_completion_callback is True
    assert hasattr(completion_func, "_target_request_function")
    assert completion_func._target_request_function == "test_request"


def test_plugin_loader_discovery():
    """Test that the plugin loader can discover decorated functions."""

    # Create a temporary Python file with decorated functions
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
from gradual.configs.decorators import request, on_call_completion

@request(name="test_request", expected_response_time=1.0)
def test_func():
    return "test"

@on_call_completion(name="test_request")
def completion_func():
    return "completed"
"""
        )
        temp_file = f.name

    try:
        # Load the plugin file
        configs = load_request_configs_from_file(temp_file)

        # Verify that RequestConfig objects were created
        assert len(configs) == 1
        config = configs[0]
        assert isinstance(config, RequestConfig)
        assert config.name == "test_request"
        assert config.expected_response_time == 1.0

        # Verify that the function and callback are stored in context
        assert "function" in config.context
        assert "completion_callback" in config.context
        assert config.context["function"].__name__ == "test_func"
        assert config.context["completion_callback"].__name__ == "completion_func"

    finally:
        # Clean up
        os.unlink(temp_file)


def test_plugin_loader_multiple_functions():
    """Test that the plugin loader can handle multiple decorated functions."""

    # Create a temporary Python file with multiple decorated functions
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
from gradual.configs.decorators import request, on_call_completion

@request(name="request1", expected_response_time=1.0)
def func1():
    return "test1"

@request(name="request2", expected_response_time=2.0)
def func2():
    return "test2"

@on_call_completion(name="request1")
def completion1():
    return "completed1"

@on_call_completion(name="request2")
def completion2():
    return "completed2"
"""
        )
        temp_file = f.name

    try:
        # Load the plugin file
        configs = load_request_configs_from_file(temp_file)

        # Verify that both RequestConfig objects were created
        assert len(configs) == 2

        # Find the configs by name
        config1 = next(c for c in configs if c.name == "request1")
        config2 = next(c for c in configs if c.name == "request2")

        assert config1.expected_response_time == 1.0
        assert config2.expected_response_time == 2.0

        # Verify callbacks are correctly associated
        assert config1.context["completion_callback"].__name__ == "completion1"
        assert config2.context["completion_callback"].__name__ == "completion2"

    finally:
        # Clean up
        os.unlink(temp_file)


def test_plugin_loader_file_not_found():
    """Test that the plugin loader raises appropriate error for missing files."""

    with pytest.raises(FileNotFoundError):
        load_request_configs_from_file("nonexistent_file.py")


def test_plugin_loader_invalid_python():
    """Test that the plugin loader handles invalid Python files gracefully."""

    # Create a temporary file with invalid Python syntax
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
invalid python syntax here
@request(name="test")
def test_func():
    return "test"
"""
        )
        temp_file = f.name

    try:
        # This should raise a syntax error
        with pytest.raises(SyntaxError):
            load_request_configs_from_file(temp_file)
    finally:
        # Clean up
        os.unlink(temp_file)
