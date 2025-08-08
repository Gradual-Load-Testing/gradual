"""
The request module provides configuration classes and utilities for managing API request
configurations in the stress testing framework. It includes support for different
request types (HTTP, WebSocket, Custom) and their specific parameters.
"""

from dataclasses import dataclass
from typing import Any, Optional

from gradual.constants.request_types import RequestType


def check_websocket_or_http(url):
    """
    Determine if a URL is for HTTP or WebSocket based on its protocol.

    This function analyzes the URL protocol to determine the appropriate request type.
    It supports both HTTP and WebSocket protocols.

    Args:
        url (str): The URL to check

    Returns:
        RequestType: The determined request type (http or websocket), or None if URL is empty

    Note:
        The function checks the protocol part of the URL (before the first ':')
        against known HTTP and WebSocket protocols.
    """
    if not url:
        return None
    url_type = url.split(":")[0]
    if url_type in RequestType.http.value:
        return RequestType.http
    if url_type in RequestType.websocket.value:
        return RequestType.websocket
    return None


@dataclass
class RequestConfig:
    """
    Configuration class for API requests in stress testing.

    This class defines the structure and parameters for individual API requests,
    supporting HTTP, WebSocket, and custom protocols. It includes validation and
    automatic type detection based on the URL, while respecting explicitly set types.

    Attributes:
        name (str): Unique identifier for this request configuration
        params (Optional[dict[str, Any]]): Parameters to be sent with the request
        http_method (str): HTTP method to use (for HTTP requests)
        expected_response_time (float): Expected response time in seconds
        context (Optional[dict[str, Any]]): Additional context for the request
        url (str): Target URL for the request
        auth (Optional[str]): Authentication method to use
        type (Optional[RequestType]): Type of request (HTTP, WebSocket, or Custom)
    """

    name: str
    params: Optional[dict[str, Any]]
    http_method: str
    expected_response_time: float
    context: Optional[dict[str, Any]] = None
    url: str = ""
    auth: Optional[str] = None
    type: Optional[RequestType] = None

    def __post_init__(self):
        """
        Post-initialization hook to set the request type based on the URL.
        Only auto-detect if no explicit type was provided or if it's the default HTTP type.
        """
        if self.context is None:
            self.context = {}

        if self.type is None:
            # Auto-detect type based on URL
            detected_type = check_websocket_or_http(self.url)
            if detected_type:
                self.type = detected_type
            else:
                # If no URL or unrecognized protocol, default to custom
                self.type = RequestType.custom
        elif self.type == RequestType.http and not self.url:
            # If explicitly set to HTTP but no URL, default to custom
            self.type = RequestType.custom
