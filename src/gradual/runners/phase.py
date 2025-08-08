"""
The phase module provides the Phase class which represents a single test phase
in the stress testing framework. A phase is a self-contained unit of testing that
can be executed independently and has its own configuration and runtime constraints.
"""

from logging import info

import gevent

from gradual.configs.phase import PhaseConfig
from gradual.reporting.stats import Stats
from gradual.runners.runner import Runner


class Phase:
    """
    Represents a single test phase in the stress testing framework.

    A phase is a self-contained unit of testing that:
    1. Has its own configuration and runtime constraints
    2. Manages its own test runner and reporting
    3. Can be executed independently of other phases
    4. Has timeout protection to prevent indefinite execution

    Attributes:
        phase_config (PhaseConfig): Configuration for this test phase
        reporting_object (Stats): Statistics and reporting handler for this phase
        runner (Runner): Test runner instance that executes the actual tests
    """

    def __init__(self, phase_config: PhaseConfig, run_name: str):
        """
        Initialize a new test phase.

        Args:
            phase_config (PhaseConfig): Configuration for this test phase
            run_name (str): Unique identifier for this test run
        """
        # Validation
        if not phase_config.name:
            raise ValueError("Phase name must not be empty")
        if phase_config.phase_runtime is not None and phase_config.phase_runtime < 0:
            raise ValueError("Phase runtime must be non-negative")
        self.phase_config = phase_config
        self.reporting_object = Stats(self.phase_config, run_name)
        self.runner = Runner(self.phase_config.scenario_config)

    def execute(self):
        """
        Execute the test phase.

        This method:
        1. Spawns a new test runner in a gevent greenlet
        2. Monitors the execution with a timeout
        3. Handles timeout conditions gracefully
        4. Manages the lifecycle of the test execution
        """
        info("Starting stats processing...")
        self.reporting_object.start_process_stats()

        info(f"Executing phase {self.phase_config.name}")

        start_test_task = gevent.spawn(self.runner.start_test)

        try:
            with gevent.Timeout(
                self.phase_config.phase_runtime,
                TimeoutError("Phase exceeded runtime."),
            ):
                gevent.wait(objects=[start_test_task])
                info("Phase run complete.")
        except TimeoutError:
            info("Runtime exceeding. stopping the phase now.")
            self.stop_phase()
        except Exception:
            self.stop_phase()
            raise

        info("Closing stats processing...")
        self.reporting_object.close_process_stats()

    def stop_phase(self):
        """
        Stop the test phase execution.

        This method:
        1. Logs the stopping of the phase
        2. Stops the test runner
        3. Confirms the phase has been stopped
        """
        info(f"Stopping Phase {self.phase_config.name}")
        self.runner.stop_runner()
        info(f"Stopped Phase {self.phase_config.name}")
