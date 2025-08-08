"""
The runner module provides the Runner class which manages the execution of test scenarios.
It coordinates multiple test scenarios running concurrently using gevent for asynchronous execution.
"""

from logging import info
from time import perf_counter_ns

import gevent

from gradual.configs.scenario import ScenarioConfig
from gradual.runners.scenario import Scenario


class Runner:
    """
    Manages the execution of multiple test scenarios concurrently.

    The Runner is responsible for:
    1. Initializing test scenarios from configurations
    2. Managing concurrent execution of scenarios using gevent
    3. Tracking execution time and running state
    4. Providing graceful shutdown capabilities

    Attributes:
        scenarios (list[Scenario]): List of initialized test scenarios
        start_counter (int): Nanosecond timestamp when the runner started
        running_scenarios (list[Scenario]): List of currently running scenarios
        running_scenarios_task (list): List of gevent tasks for running scenarios
    """

    def __init__(self, scenarios: list[ScenarioConfig]):
        """
        Initialize the test runner with scenario configurations.

        Args:
            scenarios (list[ScenarioConfig]): List of scenario configurations to run
        """
        self.scenarios = [Scenario(scenario_config) for scenario_config in scenarios]
        self.start_counter = perf_counter_ns()
        self.running_scenarios: list[Scenario] = []
        self.running_scenarios_task: list[gevent.Greenlet] = []

    def start_test(self):
        """
        Start the execution of all test scenarios.

        This method:
        1. Spawns a gevent task for each scenario
        2. Tracks running scenarios and their tasks
        3. Waits for all scenarios to complete execution
        """
        info("Executing scenarios...")

        for scenario in self.scenarios:
            self.running_scenarios.append(scenario)
            self.running_scenarios_task.append(gevent.spawn(scenario.execute))
        gevent.wait(self.running_scenarios_task)

    def stop_runner(self):
        """
        Stop all running test scenarios gracefully.

        This method:
        1. Signals all running scenarios to stop
        2. Waits for all scenario tasks to complete
        3. Ensures clean shutdown of all test activities
        """
        info("Stopping runner.")
        for scenario in self.running_scenarios:
            scenario.stop_scenario_execution = True
        gevent.wait(self.running_scenarios_task)
