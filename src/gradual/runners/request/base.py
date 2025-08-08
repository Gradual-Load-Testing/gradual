"""
The base module provides the _Request abstract base class which defines the interface
for all request implementations in the stress testing framework. This class serves as
the foundation for different types of API requests (HTTP, WebSocket, etc.).
"""

from gradual.reporting.stats import Stats
from gradual.runners.iterators import RequestIterator


class _Request:
    """
    Abstract base class for all request implementations.

    This class defines the common interface and functionality that all request types
    must implement. It provides basic infrastructure for:
    1. Managing request lifecycle
    2. Tracking request statistics
    3. Handling request iteration
    4. Supporting graceful shutdown

    Attributes:
        stop_request (bool): Flag to control request execution
        stats_instance (Stats): Statistics tracking instance
        scenario_name (str): Name of the scenario this request belongs to
        run_once (bool): Whether the request should run only once
        iterator (RequestIterator): Iterator for cycling through request configurations
    """

    def __init__(self, scenario_name: str, run_once: bool, iterator: RequestIterator):
        """
        Initialize a new request instance.

        Args:
            scenario_name (str): Name of the scenario this request belongs to
            run_once (bool): Whether the request should run only once
            iterator (RequestIterator): Iterator for cycling through request configurations
        """
        self.stop_request = False
        self.stats_instance = Stats.get_stats_instance()
        self.scenario_name = scenario_name
        self.run_once = run_once
        self.iterator = iterator

    def on_request_completion(self, *args, **kwargs):
        """
        Handle request completion events.

        This method should be implemented by subclasses to handle specific
        completion events for their request type.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Expected subclasses to implement this method.")

    def run(self):
        """
        Execute the request.

        This method should be implemented by subclasses to define the specific
        execution logic for their request type.

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Expected subclasses to implement this method.")
