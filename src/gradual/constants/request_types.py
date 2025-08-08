"""
The request_types module provides the RequestType enum which defines the supported
types of API requests in the stress testing framework. It includes HTTP and WebSocket
protocols with their respective URL schemes, plus support for custom request types.
"""

from enum import Enum


class RequestType(Enum):
    """
    Enumeration of supported API request types and their URL schemes.

    This enum defines the different types of API requests that can be made
    in the stress testing framework, along with their corresponding URL
    protocol schemes.

    Attributes:
        websocket (list[str]): List of WebSocket URL schemes (wss, ws)
        http (list[str]): List of HTTP URL schemes (http, https)
        custom (list[str]): Custom request types (empty list for any custom type)
    """

    websocket = ["wss", "ws"]
    http = ["http", "https"]
    custom: list = []  # For custom request types that don't follow URL patterns
