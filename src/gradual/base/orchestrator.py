"""
The orchestrator module provides the main coordination logic for stress testing.
It manages the execution of test phases and handles the overall test flow.
"""

from logging import info

import gevent

from gradual.configs.parser import Parser
from gradual.runners.phase import Phase


class Orchestrator:
    """
    Main orchestrator class that coordinates the execution of stress tests.

    The Orchestrator is responsible for:
    1. Loading and parsing test configurations
    2. Managing the execution of test phases
    3. Handling timing between test phases
    4. Coordinating the overall test flow

    Attributes:
        test_config_file_path (str): Path to the main test configuration file
        request_configs_path (str): Path to the request configurations file
        parser (Parser): Instance of the configuration parser
    """

    def __init__(self, test_config_file_path: str, request_configs_path: str):
        """
        Initialize the Orchestrator with configuration file paths.

        Args:
            test_config_file_path (str): Path to the main test configuration file
            request_configs_path (str): Path to the request configurations file
        """
        self.test_config_file_path = test_config_file_path
        self.request_configs_path = request_configs_path
        self.parser = Parser(self.test_config_file_path, self.request_configs_path)
        self.parser.read_configs()

    def start_stress_test(self):
        """
        Start the stress test execution.

        This method:
        1. Iterates through each phase in the test configuration
        2. Creates and executes a Phase instance for each configuration
        3. Waits for the specified time between phases
        4. Uses gevent for concurrent execution of phases
        """
        info("Starting stress test.")
        for idx, phase_config in enumerate(self.parser.phases):
            phase = Phase(phase_config, self.parser.run_name)
            running_phase = gevent.spawn(phase.execute)
            gevent.wait([running_phase])

            if idx < len(self.parser.phases) - 1:
                info(
                    f"waiting for {self.parser.phase_wait} secs before starting new phase."
                )
                gevent.sleep(self.parser.phase_wait)
