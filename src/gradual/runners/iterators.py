"""
The iterators module provides the RequestIterator class which manages cycling through
different request configurations in a round-robin fashion. This is used to distribute
load across different types of API requests during stress testing.
"""

from dataclasses import dataclass
from typing import Optional
from gradual.configs.request import RequestConfig


@dataclass
class RequestIterator:
    """
    Iterator for cycling through different request configurations.

    This class provides a round-robin mechanism to cycle through different types
    of API requests during stress testing. It maintains the current position and
    provides methods to get the next request configuration.

    Attributes:
        request_types (list[RequestConfig]): List of request configurations to cycle through
        request_type_index (int): Current index in the request_types list
        current (int): Index of the last returned request type, None if no requests have been returned
    """

    request_types: list[RequestConfig]
    request_type_index: int = 0
    current: Optional[int] = None

    def get_next_request(self):
        """
        Get the next request configuration in the round-robin sequence.

        Returns:
            RequestConfig: The next request configuration to use

        Note:
            This method cycles through the request_types list in a round-robin fashion,
            returning to the beginning when it reaches the end.
        """
        self.current = self.request_type_index
        request_type = self.request_types[self.request_type_index]
        self.request_type_index += 1
        self.request_type_index %= len(self.request_types)
        return request_type

    @property
    def current_request(self):
        """
        Get the current request configuration.

        Returns:
            RequestConfig: The current request configuration, or None if no requests have been returned yet
        """
        if self.current is not None:
            return self.request_types[self.current]
        return None
