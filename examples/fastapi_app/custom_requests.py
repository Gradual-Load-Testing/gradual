"""
Example custom request functions using the @request and @on_call_completion decorators.

This file demonstrates how to create custom request functions that can be loaded
by the gradual stress testing framework.
"""

import time

import requests

from gradual.configs.decorators import on_call_completion, request


@request(
    name="custom_get_request",
    url="http://localhost:8000/api/items",
    http_method="get",
    expected_response_time=1.0,
)
def get_items():
    """Custom GET request to fetch items."""
    response = requests.get("http://localhost:8000/api/items")
    return response.json()


@on_call_completion(name="custom_get_request")
def get_items_complete():
    """Completion callback for get_items request."""
    print("GET items request completed")
    # Here you could persist stats to database
    # persist_stats()


@request(
    name="custom_post_request",
    url="http://localhost:8000/api/items",
    http_method="post",
    params={"name": "test_item", "description": "Test item for stress testing"},
    expected_response_time=2.0,
)
def create_item():
    """Custom POST request to create an item."""
    data = {"name": "test_item", "description": "Test item for stress testing"}
    response = requests.post("http://localhost:8000/api/items", json=data)
    return response.json()


@on_call_completion(name="custom_post_request")
def create_item_complete():
    """Completion callback for create_item request."""
    print("POST create item request completed")
    # Here you could persist stats to database
    # persist_stats()


@request(
    name="custom_websocket_request",
    url="ws://localhost:8000/ws",
    expected_response_time=0.5,
    type="websocket",
)
def websocket_connection():
    """Custom WebSocket connection request."""
    # This would be implemented with a WebSocket client
    # For now, just simulate a connection
    time.sleep(0.1)
    return {"status": "connected"}


@on_call_completion(name="custom_websocket_request")
def websocket_complete():
    """Completion callback for websocket_connection request."""
    print("WebSocket connection request completed")
    # Here you could persist stats to database
    # persist_stats()


@request(name="simple_function", expected_response_time=0.1)
def simple_function():
    """A simple function without HTTP request."""
    # This could be any custom logic
    result = {"message": "Hello from custom function", "timestamp": time.time()}
    return result


@on_call_completion(name="simple_function")
def simple_function_complete():
    """Completion callback for simple_function."""
    print("Simple function completed")
    # Here you could persist stats to database
    # persist_stats()
