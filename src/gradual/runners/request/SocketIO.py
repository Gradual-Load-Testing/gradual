"""
The SocketIO module provides the SocketRequest class which implements WebSocket-based
API requests for stress testing. It supports WebSocket connections, message sending,
and response tracking.
"""

from gradual.runners.request.base import _Request
from logging import debug, error
import gevent
import json
from time import time_ns
import traceback
import uuid
from websocket import create_connection
from functools import cache
from gradual.configs.request import RequestConfig


class SocketRequest(_Request):
    """
    Implementation of WebSocket-based API requests for stress testing.

    This class provides functionality for:
    1. Establishing and managing WebSocket connections
    2. Sending messages through WebSocket
    3. Receiving and processing responses
    4. Tracking connection and message timing
    5. Handling connection errors and failures

    Note:
        The class uses caching for WebSocket connections to improve performance
        and reduce connection overhead.
    """

    def on_request_completion(
        self,
        request_type: RequestConfig,
        response: tuple,
        response_time,
        start_time,
        end_time,
        params,
    ):
        """
        Handle WebSocket request completion and record statistics.

        This method is called after each WebSocket interaction completes to:
        1. Collect response data and timing information
        2. Record statistics for analysis
        3. Log debug information

        Args:
            request_type (RequestConfig): Configuration for this request
            response (tuple): Tuple containing (status_code, response_message)
            response_time: Time taken for the interaction in nanoseconds
            start_time: Start time of the interaction in nanoseconds
            end_time: End time of the interaction in nanoseconds
            params (dict): Parameters used in the message
        """
        stat_data = {
            "request_name": request_type.name,
            "url": request_type.url,
            "params": params,
            "context": request_type.context,
            "response_time": response_time,
            "status_code": response[0],
            "start_time": start_time,
            "end_time": end_time,
            "iid": params["iid"],
            "scenario_name": self.scenario_name,
            "expected_response_time": request_type.expected_response_time,
        }

        debug(stat_data)
        self.stats_instance.persist_stats(stat_data)

    @cache
    def create_ws_connection(url):
        """
        Create a WebSocket connection to the specified URL.

        This method is cached to reuse connections and improve performance.
        It handles connection errors and provides detailed error logging.

        Args:
            url (str): WebSocket server URL to connect to

        Returns:
            WebSocket: Established WebSocket connection

        Raises:
            Exception: If connection fails, with detailed error information
        """
        try:
            ws = create_connection(url)
        except Exception as e:
            error(f"web socket failed to secure a connection with error: {e}")
            error(traceback.format_exc())
            raise e
        return ws

    def run(self):
        """
        Execute the WebSocket request in a loop until stopped.

        This method:
        1. Establishes WebSocket connections
        2. Sends messages in a loop until stop_request is True
        3. Receives and processes responses
        4. Tracks timing and response data
        5. Handles connection errors and failures
        6. Closes connections when done

        Note:
            The method will exit after a single interaction if run_once is True.
            It handles both successful and failed message sending/receiving scenarios.
        """
        while not self.stop_request:
            iid = str(uuid.uuid4())
            request_type = self.handler.get_next_request()
            ws = self.create_ws_connection(request_type.url)
            data = request_type.params | {"iid": iid}
            start_time = time_ns()
            response_code = 200
            response = None
            is_sent = False
            try:
                ws.send(json.dumps(request_type.params))
                is_sent = True
            except Exception as e:
                response_code = 503
                error(
                    f"Failed sending the message through websocket connection with error: {e}"
                )
                error(traceback.format_exc())

            try:
                if is_sent:
                    response = ws.recv()
            except Exception as e:
                response_code = 500
                error(
                    f"Failed receiving the message through websocket connection with error: {e}"
                )
                error(traceback.format_exc())
            finally:
                if response is not None and "Success" not in response:
                    error(response)
                end_time = time_ns()
                response_time_ns = end_time - start_time
                gevent.spawn(
                    self.on_request_completion,
                    request_type,
                    (response_code, response),
                    response_time_ns,
                    start_time,
                    end_time,
                    data,
                )
                if self.run_once:
                    self.stop_request = True
                    break
        ws.close()
