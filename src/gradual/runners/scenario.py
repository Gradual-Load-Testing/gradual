"""
The scenario module provides the Scenario class which manages the execution of test requests
within a scenario. It handles concurrency, ramp-up, and different types of requests (HTTP, WebSocket).
"""

from logging import info

import gevent
from tabulate import tabulate

from gradual.configs.scenario import ScenarioConfig
from gradual.constants.request_types import RequestType
from gradual.runners.iterators import RequestIterator
from gradual.runners.request.base import _Request
from gradual.runners.request.Http import HttpRequest
from gradual.runners.request.SocketIO import SocketRequest
from gradual.runners.session import HTTPSession


class Scenario:
    """
    Manages the execution of test requests within a scenario.

    The Scenario class is responsible for:
    1. Managing concurrent execution of test requests
    2. Handling ramp-up of concurrent requests
    3. Supporting different types of requests (HTTP, WebSocket)
    4. Managing test sessions and iterators
    5. Providing graceful shutdown capabilities

    Attributes:
        scenario_config (ScenarioConfig): Configuration for this test scenario
        running_request_tasks (list[gevent.Greenlet]): List of currently running request tasks
        last_request_idx (int): Index of the last request type used
        stop_scenario_execution (bool): Flag to control scenario execution
        requests (list[_Request]): List of request instances
        iterator (RequestIterator, optional): Iterator for cycling through request types
    """

    def __init__(self, scenario_config: ScenarioConfig):
        """
        Initialize a new test scenario.

        Args:
            scenario_config (ScenarioConfig): Configuration for this test scenario
        """
        self.scenario_config = scenario_config
        self.running_request_tasks: list[gevent.Greenlet] = []
        self.last_request_idx: int = 0
        self.stop_scenario_execution = False
        self.requests: list[_Request] = []
        self.iterator = None
        if self.scenario_config.iterate_through_requests:
            self.iterator = RequestIterator(
                request_types=self.scenario_config.request_configs
            )

    def do_ramp_up(self, ramp_up_value):
        """
        Increase the number of concurrent requests up to the specified value.

        This method:
        1. Creates new request instances based on the request type
        2. Manages HTTP sessions for HTTP requests
        3. Spawns new gevent tasks for each request
        4. Tracks running requests and their tasks

        Args:
            ramp_up_value (int): Target number of concurrent requests to achieve
        """
        if self.scenario_config.run_once:
            self.running_request_tasks = []
        session = None
        current_concurrency = 0
        total_request_configs = len(self.scenario_config.request_configs)
        request_type_idx = self.last_request_idx % total_request_configs

        while current_concurrency < ramp_up_value:
            current_request_type = self.scenario_config.request_configs[
                request_type_idx
            ]
            if not self.scenario_config.iterate_through_requests:
                iterator = RequestIterator(
                    request_types=[
                        self.scenario_config.request_configs[request_type_idx]
                    ]
                )
            else:
                iterator = self.iterator
            if current_request_type.type == RequestType.http:
                if session is None:
                    session = HTTPSession(
                        pool_connections=ramp_up_value, pool_maxsize=ramp_up_value
                    )
                request = HttpRequest(
                    scenario_name=self.scenario_config.name,
                    session=session,
                    run_once=self.scenario_config.run_once,
                    iterator=iterator,
                )
            elif current_request_type.type == RequestType.websocket:
                request = SocketRequest(
                    scenario_name=self.scenario_config.name,
                    run_once=self.scenario_config.run_once,
                    iterator=iterator,
                )
            else:
                # Create a dynamic _Request subclass with the user's run function
                custom_function = current_request_type.context.get("function")
                completion_callback = current_request_type.context.get(
                    "completion_callback"
                )

                if custom_function:
                    # Create a dynamic class that inherits from _Request
                    class CustomRequestClass(_Request):
                        def run(self):
                            return custom_function()  # noqa: B023

                        def on_request_completion(self, *args, **kwargs):
                            if completion_callback:  # noqa: B023
                                completion_callback()  # noqa: B023

                    request = CustomRequestClass(
                        scenario_name=self.scenario_config.name,
                        run_once=self.scenario_config.run_once,
                        iterator=iterator,
                    )

                else:
                    request = _Request(
                        scenario_name=self.scenario_config.name,
                        run_once=self.scenario_config.run_once,
                        iterator=iterator,
                    )

            self.running_request_tasks.append(gevent.spawn(request.run))
            current_concurrency += 1
            self.requests.append(request)
            if len(self.running_request_tasks) >= self.scenario_config.max_concurrency:
                return
            self.last_request_idx = request_type_idx

            request_type_idx += 1
            request_type_idx %= total_request_configs

    def execute(self):
        """
        Execute the test scenario with configured ramp-up behavior.

        This method:
        1. Starts with minimum concurrency
        2. Gradually increases concurrency based on ramp-up configuration
        3. Handles both run-once and continuous execution modes
        4. Manages wait times between ramp-ups
        5. Provides detailed logging of execution progress
        """
        info(
            f"Starting the testiung with minimum concurrency i.e., "
            f"{self.scenario_config.min_concurrency}, scenario: {self.scenario_config.name}"
        )

        # Current index of ramp up and ramp up wait array.
        ramp_up_idx = 0
        ramp_up_wait_idx = 0

        # Starting with minimum no. of requests
        self.do_ramp_up(self.scenario_config.min_concurrency)
        if not self.scenario_config.run_once:
            gevent.sleep(self.scenario_config.ramp_up_wait[ramp_up_wait_idx])
        else:
            gevent.wait(self.running_request_tasks)

        # Starting request with ramp up and ramp up wait.
        while not self.stop_scenario_execution:
            # Increasing ramp_up_wait_index
            ramp_up_wait_idx += 1
            if ramp_up_wait_idx >= len(self.scenario_config.ramp_up_wait):
                ramp_up_wait_idx = len(self.scenario_config.ramp_up_wait) - 1

            # Calculating by how much we have to ramp up in this iteration.
            if self.scenario_config.multiply:
                # Suppose we want to ramp up the total requests by 2x and
                # there are already x requests running in an infinite loop.
                # Then, total requests need to be added is
                # 2x = already_running_request(x) * (multiplication_facotr(2) -1 )
                # to make the concurrency 2x.
                if not self.scenario_config.run_once:
                    ramp_up_val = len(self.running_request_tasks) * (
                        self.scenario_config.ramp_up[ramp_up_idx] - 1
                    )

                # Suppose we want to ramp up the total requests by 2x and
                # there are already x requests with run_once True.
                # That means we are ramping up after the requests are completed.
                # Then, total requests needs to be added is
                # 2x = already_running_request(x) * (multiplication_facotr(2))
                # to make the concurrency 2x.
                else:
                    ramp_up_val = len(self.running_request_tasks) * (
                        self.scenario_config.ramp_up[ramp_up_idx]
                    )

            else:
                if not self.scenario_config.run_once:
                    ramp_up_val = self.scenario_config.ramp_up[ramp_up_idx]
                else:
                    ramp_up_val = (
                        len(self.running_request_tasks)
                        + self.scenario_config.ramp_up[ramp_up_idx]
                    )
            # Ramping up by ramp_up nos.
            if len(self.running_request_tasks) < self.scenario_config.max_concurrency:
                # Logging before ramp_up.
                table = [
                    [
                        len(self.running_request_tasks),
                        self.scenario_config.name,
                        ramp_up_val,
                    ]
                ]
                info(
                    tabulate(
                        table,
                        headers=[
                            "Current no. of requests",
                            "Scenario Name",
                            "Next ramp up value",
                        ],
                    )
                )
                self.do_ramp_up(ramp_up_value=ramp_up_val)

            if self.stop_scenario_execution:
                self.stop_scenario()
                break

            if not self.scenario_config.run_once:
                # Waiting for ramp_up wait secs before ramping up
                gevent.sleep(self.scenario_config.ramp_up_wait[ramp_up_wait_idx])
            else:
                # waitng for the running requests to finish.
                gevent.wait(self.running_request_tasks)

            # Increasing ramp_up_index
            ramp_up_idx += 1
            if ramp_up_idx >= len(self.scenario_config.ramp_up):
                ramp_up_idx = len(self.scenario_config.ramp_up) - 1

        if self.stop_scenario_execution:
            self.stop_scenario()

        if len(self.running_request_tasks):
            gevent.wait(self.running_request_tasks)

    def stop_scenario(self):
        """
        Stop the scenario execution gracefully.

        This method:
        1. Sets the stop flag for the scenario
        2. Signals all running requests to stop
        3. Ensures clean shutdown of all test activities
        """
        info(f"Stopping scenario {self.scenario_config.name}")
        self.stop_scenario_execution = True
        for request in self.requests:
            request.stop_request = True
