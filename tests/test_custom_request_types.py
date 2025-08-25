"""
Tests for custom request types functionality.
"""

import os
import tempfile

from gradual.configs.decorators import request
from gradual.configs.plugin_loader import load_request_configs_from_file
from gradual.configs.request import RequestConfig
from gradual.constants.request_types import RequestType


def test_custom_request_type_without_url():
    """Test that custom request types work without URLs."""

    # Create a temporary Python file with custom request functions
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            '''
from gradual.configs.decorators import request, on_call_completion

@request(
    name="database_query",
    type="custom",
    expected_response_time=0.5
)
def query_database():
    """Custom database query operation."""
    return {"result": "data", "rows": 100}

@on_call_completion(name="database_query")
def db_completion():
    return "Database query completed"

@request(
    name="file_operation",
    type="custom",
    expected_response_time=1.0
)
def process_file():
    """Custom file processing operation."""
    return {"status": "processed", "files": 5}

@on_call_completion(name="file_operation")
def file_completion():
    return "File processing completed"
'''
        )
        temp_file = f.name

    try:
        # Load the plugin file
        configs = load_request_configs_from_file(temp_file)

        # Verify that RequestConfig objects were created
        assert len(configs) == 2

        # Check database query config
        db_config = next(c for c in configs if c.name == "database_query")
        assert db_config.type == RequestType.custom
        assert db_config.url == ""
        assert db_config.expected_response_time == 0.5
        assert db_config.context["function"].__name__ == "query_database"
        assert db_config.context["completion_callback"].__name__ == "db_completion"

        # Check file operation config
        file_config = next(c for c in configs if c.name == "file_operation")
        assert file_config.type == RequestType.custom
        assert file_config.url == ""
        assert file_config.expected_response_time == 1.0
        assert file_config.context["function"].__name__ == "process_file"
        assert file_config.context["completion_callback"].__name__ == "file_completion"

    finally:
        # Clean up
        os.unlink(temp_file)


def test_mixed_request_types():
    """Test mixing HTTP, WebSocket, and custom request types."""

    # Create a temporary Python file with mixed request types
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
from gradual.configs.decorators import request, on_call_completion

@request(
    name="http_request",
    url="http://api.example.com/users",
    type="http",
    http_method="get",
    expected_response_time=1.0
)
def http_request():
    return {"users": []}

@request(
    name="websocket_request",
    url="ws://api.example.com/ws",
    type="websocket",
    expected_response_time=0.5
)
def websocket_request():
    return {"connected": True}

@request(
    name="custom_request",
    type="custom",
    expected_response_time=0.3
)
def custom_request():
    return {"custom": "result"}

@on_call_completion(name="http_request")
def http_completion():
    return "HTTP request completed"

@on_call_completion(name="websocket_request")
def ws_completion():
    return "WebSocket request completed"

@on_call_completion(name="custom_request")
def custom_completion():
    return "Custom request completed"
"""
        )
        temp_file = f.name

    try:
        # Load the plugin file
        configs = load_request_configs_from_file(temp_file)

        # Verify that all RequestConfig objects were created
        assert len(configs) == 3

        # Check HTTP request
        http_config = next(c for c in configs if c.name == "http_request")
        assert http_config.type == RequestType.http
        assert http_config.url == "http://api.example.com/users"
        assert http_config.http_method == "get"

        # Check WebSocket request
        ws_config = next(c for c in configs if c.name == "websocket_request")
        assert ws_config.type == RequestType.websocket
        assert ws_config.url == "ws://api.example.com/ws"

        # Check custom request
        custom_config = next(c for c in configs if c.name == "custom_request")
        assert custom_config.type == RequestType.custom
        assert custom_config.url == ""

    finally:
        # Clean up
        os.unlink(temp_file)


def test_auto_detection_with_custom_override():
    """Test that explicit type overrides auto-detection."""

    # Create a temporary Python file with custom type override
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
from gradual.configs.decorators import request

@request(
    name="custom_http",
    url="http://api.example.com/data",
    type="custom",  # Explicitly set to custom despite HTTP URL
    expected_response_time=1.0
)
def custom_http_request():
    return {"custom": "http-like"}
"""
        )
        temp_file = f.name

    try:
        # Load the plugin file
        configs = load_request_configs_from_file(temp_file)

        # Verify that the type is custom despite HTTP URL
        assert len(configs) == 1
        config = configs[0]
        assert config.type == RequestType.custom
        assert config.url == "http://api.example.com/data"

    finally:
        # Clean up
        os.unlink(temp_file)


def test_unknown_type_defaults_to_custom():
    """Test that unknown types default to custom."""

    # Create a temporary Python file with unknown type
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
from gradual.configs.decorators import request

@request(
    name="unknown_type",
    type="unknown_type",  # Unknown type
    expected_response_time=1.0
)
def unknown_request():
    return {"unknown": "type"}
"""
        )
        temp_file = f.name

    try:
        # Load the plugin file
        configs = load_request_configs_from_file(temp_file)

        # Verify that unknown type defaults to custom
        assert len(configs) == 1
        config = configs[0]
        assert config.type == RequestType.custom

    finally:
        # Clean up
        os.unlink(temp_file)


def test_custom_request_execution():
    """Test that custom request functions can be executed."""

    @request(name="test_custom", type="custom", expected_response_time=0.1)
    def test_function():
        return {"message": "Hello from custom function"}

    # Create RequestConfig manually to test execution
    config = RequestConfig(
        name="test_custom",
        params={},
        http_method="get",
        expected_response_time=0.1,
        context={"function": test_function},
        type=RequestType.custom,
    )

    # Execute the function
    result = config.context["function"]()
    assert result == {"message": "Hello from custom function"}
    assert config.type == RequestType.custom
