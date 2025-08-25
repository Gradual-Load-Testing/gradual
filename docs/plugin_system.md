# Plugin System for Custom Request Functions

The gradual stress testing framework now supports a plugin system that allows you to define custom request functions using Python decorators. This system enables you to create complex, custom request logic while maintaining the framework's configuration-driven approach.

## Overview

The plugin system consists of two main components:

1. **Decorators**: `@request` and `@on_call_completion` decorators for marking functions
2. **Plugin Loader**: Automatic discovery and loading of decorated functions from Python files

## Decorators

### @request Decorator

The `@request` decorator marks a function as a request function that can be executed during stress testing.

```python
from gradual.configs.decorators import request

@request(
    name="my_custom_request",
    url="http://api.example.com/endpoint",
    http_method="post",
    params={"key": "value"},
    expected_response_time=1.5,
    auth="bearer",
    type="http"
)
def my_request_function():
    # Your custom request logic here
    import requests
    response = requests.post("http://api.example.com/endpoint", json={"key": "value"})
    return response.json()
```

**Parameters:**

- `name` (str, optional): Custom name for the request (defaults to function name)
- `url` (str): Target URL for the request
- `params` (dict, optional): Parameters to be sent with the request
- `http_method` (str): HTTP method to use (default: "get")
- `expected_response_time` (float): Expected response time in seconds (default: 1.0)
- `auth` (str, optional): Authentication method to use
- `type` (str, optional): Type of request (http, websocket, etc.)

### @on_call_completion Decorator

The `@on_call_completion` decorator marks a function as a completion callback that will be executed after a specific request function completes.

```python
from gradual.configs.decorators import on_call_completion

@on_call_completion(name="my_custom_request")
def my_completion_callback():
    # This function will be called after my_custom_request completes
    print("Request completed!")
    # You can add logic here like:
    # - Persisting statistics to database
    # - Logging results
    # - Triggering follow-up actions
```

**Parameters:**

- `name` (str): Name of the request function this callback is associated with

## Using Python Files in Configuration

To use custom request functions in your stress test configuration, you can reference a Python file using the `FROM_REQUEST_YAML_FILE` key:

```yaml
runs:
  name: "Custom Requests Test"
  phases:
    "phase1":
      scenarios:
        "custom_scenario":
          requests: "FROM_REQUEST_YAML_FILE"
          request_file: "path/to/your/requests.py"
          min_concurrency: 1
          max_concurrency: 10
          ramp_up_multiply: [1, 2, 3]
          ramp_up_wait: [1, 1, 1]
          iterate_through_requests: true
      run_time: 60
```

The framework will automatically:

1. Load the Python file
2. Discover all functions decorated with `@request`
3. Create `RequestConfig` objects from these functions
4. Associate completion callbacks with their respective request functions

## Example: Complete Custom Request File

Here's a complete example of a Python file with custom request functions:

```python
# custom_requests.py
import time
import requests
from gradual.configs.decorators import request, on_call_completion

@request(
    name="get_user_data",
    url="http://api.example.com/users",
    http_method="get",
    expected_response_time=1.0
)
def fetch_user_data():
    """Fetch user data from API."""
    response = requests.get("http://api.example.com/users")
    return response.json()

@on_call_completion(name="get_user_data")
def user_data_completed():
    """Callback when user data request completes."""
    print("User data request completed")
    # Add your completion logic here

@request(
    name="create_user",
    url="http://api.example.com/users",
    http_method="post",
    params={"name": "Test User", "email": "test@example.com"},
    expected_response_time=2.0
)
def create_new_user():
    """Create a new user."""
    data = {"name": "Test User", "email": "test@example.com"}
    response = requests.post("http://api.example.com/users", json=data)
    return response.json()

@on_call_completion(name="create_user")
def user_created():
    """Callback when user creation completes."""
    print("User creation completed")

@request(
    name="websocket_connection",
    url="ws://api.example.com/ws",
    expected_response_time=0.5,
    type="websocket"
)
def connect_websocket():
    """Establish WebSocket connection."""
    # WebSocket implementation would go here
    time.sleep(0.1)  # Simulate connection time
    return {"status": "connected"}

@on_call_completion(name="websocket_connection")
def websocket_connected():
    """Callback when WebSocket connects."""
    print("WebSocket connection established")
```

## Configuration File Example

```yaml
# test_config.yaml
runs:
  name: "Custom API Test"
  wait_between_phases: 5
  phases:
    "api_testing":
      scenarios:
        "user_operations":
          requests: "FROM_REQUEST_YAML_FILE"
          request_file: "custom_requests.py"
          min_concurrency: 1
          max_concurrency: 5
          ramp_up_multiply: [1, 2, 3]
          ramp_up_wait: [2, 2, 2]
          iterate_through_requests: true
      run_time: 30
```

## Advanced Usage

### Custom Logic Without HTTP Requests

You can create request functions that don't make HTTP requests but perform custom logic:

```python
@request(
    name="data_processing",
    expected_response_time=0.5
)
def process_data():
    """Process data without making HTTP requests."""
    # Your custom processing logic here
    result = {"processed": True, "timestamp": time.time()}
    return result

@on_call_completion(name="data_processing")
def processing_completed():
    """Callback when data processing completes."""
    print("Data processing completed")
```

### Dynamic Parameters

You can use dynamic parameters in your request functions:

```python
@request(
    name="dynamic_request",
    url="http://api.example.com/dynamic",
    expected_response_time=1.0
)
def dynamic_request():
    """Request with dynamic parameters."""
    # Generate dynamic parameters
    timestamp = int(time.time())
    params = {"timestamp": timestamp, "random": random.randint(1, 100)}

    response = requests.get("http://api.example.com/dynamic", params=params)
    return response.json()
```

## Best Practices

1. **Function Names**: Use descriptive function names that indicate what the request does
2. **Error Handling**: Include proper error handling in your request functions
3. **Completion Callbacks**: Use completion callbacks for logging, statistics, or cleanup
4. **Documentation**: Add docstrings to your request functions for clarity
5. **Modular Design**: Keep related requests in the same file for better organization

## Integration with Existing Framework

The plugin system integrates seamlessly with the existing gradual framework:

- RequestConfig objects created from decorated functions have the same structure as YAML-defined requests
- Completion callbacks are stored in the request context and can be executed by the framework
- All existing framework features (concurrency, ramp-up, timing) work with custom request functions
- The framework handles execution, timing, and statistics collection automatically
