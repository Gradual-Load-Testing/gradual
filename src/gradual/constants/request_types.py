"""
The request_types module provides the RequestType enum which defines the supported
types of API requests in the stress testing framework. It includes HTTP and WebSocket
protocols with their respective URL schemes.
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
    """

    websocket = ["wss", "ws"]
    http = ["http", "https"]
