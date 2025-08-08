"""
The Http module provides the HttpRequest class which implements HTTP-based API requests
for stress testing. It supports various HTTP methods, authentication mechanisms,
and response tracking.
"""

from gradual.runners.request.base import _Request
from gradual.runners.session import HTTPSession
import gevent
from requests import Response
from gradual.runners.iterators import RequestIterator
from logging import debug, error, warning, info
from time import time_ns
import traceback
import uuid
from gradual.configs.request import RequestConfig


class HttpRequest(_Request):
    """
    Implementation of HTTP-based API requests for stress testing.

    This class provides functionality for:
    1. Making HTTP requests with different methods (GET, POST, PUT, DELETE)
    2. Supporting Kerberos authentication
    3. Tracking response times and status codes
    4. Managing request sessions and connection pooling
    5. Handling request completion and statistics

    Attributes:
        session (HTTPSession): HTTP session for making requests
        _kerberos_available (bool): Whether Kerberos support is available
        _kerberos_auth (HTTPKerberosAuth or None): Cached Kerberos auth handler
    """

    def __init__(
        self,
        scenario_name: str,
        session: HTTPSession,
        run_once: bool,
        iterator: RequestIterator,
    ):
        """
        Initialize a new HTTP request instance.

        Args:
            scenario_name (str): Name of the scenario this request belongs to
            session (HTTPSession): HTTP session for making requests
            run_once (bool): Whether the request should run only once
            iterator (RequestIterator): Iterator for cycling through request configurations
        """
        super().__init__(
            scenario_name=scenario_name, run_once=run_once, iterator=iterator
        )
        self.session = session
        self._kerberos_available = None
        self._kerberos_auth = None

    def _check_kerberos_availability(self):
        """
        Check if Kerberos support is available and cache the result.

        Returns:
            bool: True if Kerberos support is available, False otherwise
        """
        if self._kerberos_available is not None:
            return self._kerberos_available

        try:
            from requests_kerberos import DISABLED, HTTPKerberosAuth

            self._kerberos_auth = HTTPKerberosAuth(mutual_authentication=DISABLED)
            self._kerberos_available = True
            info("Kerberos authentication support is available")
            return True
        except ImportError:
            self._kerberos_available = False
            warning(
                "Kerberos authentication support is not available. "
                "Install it with: pip install -e .[kerberos]"
            )
            return False
        except Exception as e:
            self._kerberos_available = False
            error(f"Error initializing Kerberos support: {str(e)}")
            return False

    def requires_kerberos(self, request_type: RequestConfig) -> bool:
        """
        Check if a request requires Kerberos authentication.

        Args:
            request_type (RequestConfig): The request configuration to check

        Returns:
            bool: True if the request requires Kerberos authentication
        """
        return request_type.auth == "kerb"

    def get_kerberos_auth(self):
        """
        Get Kerberos authentication handler if available.

        Returns:
            HTTPKerberosAuth or None: Kerberos authentication handler if available,
                                    None if Kerberos support is not installed.
        """
        if not self._check_kerberos_availability():
            return None
        return self._kerberos_auth

    def send_request(self, request_type: RequestConfig, req_kwargs):
        """
        Send an HTTP request based on the request configuration.

        This method supports different HTTP methods and handles the actual
        request sending using the configured session.

        Args:
            request_type (RequestConfig): Configuration for this request
            req_kwargs (dict): Keyword arguments for the request

        Returns:
            Response: The HTTP response from the server

        Raises:
            ValueError: If an unsupported HTTP method is specified
        """
        method = request_type.http_method.lower()

        if method == "get":
            return self.session.get(**req_kwargs)

        if method == "post":
            return self.session.post(**req_kwargs)

        if method == "put":
            return self.session.put(**req_kwargs)

        if method == "delete":
            return self.session.delete(**req_kwargs)

        else:
            raise ValueError("Unsupported HTTP method")

    def on_request_completion(
        self,
        request_type: RequestConfig,
        response: Response,
        response_time,
        start_time,
        end_time,
        params,
    ):
        """
        Handle HTTP request completion and record statistics.

        This method is called after each HTTP request completes to:
        1. Collect response data and timing information
        2. Record statistics for analysis
        3. Log debug information

        Args:
            request_type (RequestConfig): Configuration for this request
            response (Response): The HTTP response from the server
            response_time: Time taken for the request in nanoseconds
            start_time: Start time of the request in nanoseconds
            end_time: End time of the request in nanoseconds
            params (dict): Parameters used in the request
        """
        stat_data = {
            "request_name": request_type.name,
            "url": request_type.url,
            "params": params,
            "context": request_type.context,
            "response_time": response_time,
            "status_code": response.status_code,
            "start_time": start_time,
            "end_time": end_time,
            "iid": params["iid"],
            "scenario_name": self.scenario_name,
            "expected_response_time": request_type.expected_response_time,
        }

        debug(stat_data)
        self.stats_instance.persist_stats(stat_data)

    def run(self):
        """
        Execute the HTTP request in a loop until stopped.

        This method:
        1. Makes HTTP requests in a loop until stop_request is True
        2. Handles request preparation and sending
        3. Tracks timing and response data
        4. Manages authentication and headers
        5. Handles errors and exceptions
        6. Closes the session when done

        Note:
            The method will exit after a single request if run_once is True.
        """
        while not self.stop_request:
            try:
                iid = str(uuid.uuid4())
                request_type = self.iterator.get_next_request()
                data = request_type.params | {"iid": iid}
                req_kwargs = {
                    "headers": {
                        "X-ANTICSRF-HEADER": "DESCO",
                        "Content-type": "application/json",
                    },
                    "json": data,
                    "url": request_type.url,
                }

                # Handle Kerberos authentication
                if self.requires_kerberos(request_type):
                    auth = self.get_kerberos_auth()
                    if auth:
                        req_kwargs["auth"] = auth
                    else:
                        raise Exception(
                            f"Skipping request '{request_type.name}' due to missing Kerberos authentication"
                        )

                start_time = time_ns()
                response = self.send_request(
                    request_type=request_type, req_kwargs=req_kwargs
                )
                end_time = time_ns()
                response_time_ns = end_time - start_time
                gevent.spawn(
                    self.on_request_completion,
                    request_type,
                    response,
                    response_time_ns,
                    start_time,
                    end_time,
                    data,
                )
            except Exception as e:
                error(
                    f"Error in request '{request_type.name if 'request_type' in locals() else 'unknown'}': {str(e)}"
                )
                error(traceback.format_exc())

            if self.run_once:
                self.stop_request = True
                break
        self.session.close()
