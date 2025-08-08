"""
The parser module provides the Parser class which handles loading and parsing
configuration files for stress testing. It supports YAML configuration files
and validates the configuration structure.
"""

from dataclasses import dataclass, field
from logging import info
from pathlib import Path

import yaml

from gradual.configs.request import RequestConfig
from gradual.configs.scenario import ScenarioConfig
from gradual.configs.phase import PhaseConfig
from gradual.configs.validate import assert_not_empty, validate_min_concurrency


def convert_list(val):
    """
    Convert a single value to a list if it's not already a list.

    This utility function ensures that values that should be lists are always
    in list format, converting single values to single-item lists.

    Args:
        val: Value to convert (int or list)

    Returns:
        list: The input value as a list
    Raises:
        TypeError: If the value is not an int or list
    """
    if isinstance(val, int):
        return [val]
    if isinstance(val, list):
        return val
    raise TypeError(f"Expected int or list, got {type(val).__name__}: {val}")


@dataclass
class Parser:
    """
    Configuration parser for stress testing setup.

    This class handles loading and parsing of configuration files, including:
    1. Test configuration files
    2. Request configuration files
    3. Parameter configuration files

    It validates the configuration structure and creates appropriate configuration
    objects for phases, scenarios, and requests.

    Attributes:
        test_config_file_path (str): Path to the main test configuration file
        request_configs_path (str): Path to the request configurations file
        run_name (str | None): Name of the test run
        phases (list[PhaseConfig]): List of parsed phase configurations
        phase_wait (int): Wait time between phases in seconds
    """

    test_config_file_path: str
    request_configs_path: str
    run_name: str | None = None
    phases: list[PhaseConfig] = field(default_factory=list)
    phase_wait: int = 0

    @staticmethod
    def read_request_file(file_path: Path):
        """
        Read and parse a request configuration file.

        This method reads a YAML file containing request configurations and creates
        RequestConfig objects for each request definition. It validates required fields
        and handles optional parameters.

        Args:
            file_path (Path): Path to the request configuration file

        Returns:
            list[RequestConfig]: List of parsed request configurations

        Raises:
            AssertionError: If required fields are missing
        """
        request_config = []
        with file_path.open("r") as request_file:
            requests = yaml.safe_load(request_file)
            assert_not_empty("requests", requests.get("requests"))
            for request_name, request in requests["requests"].items():
                assert_not_empty(
                    "params",
                    request.get("params"),
                    f"Please provide params for request: {request}.",
                )
                assert_not_empty(
                    "method",
                    request.get("method"),
                    f"Please provide method for request: {request}.",
                )
                assert_not_empty(
                    "expected_response_time",
                    request.get("expected_response_time"),
                    f"Please provide expected_response_time for request: {request}.",
                )
                config = RequestConfig(
                    name=request_name,
                    url=request.get("url", ""),
                    params=request.get("params", {}),
                    http_method=request.get("method", "get"),
                    expected_response_time=request.get("expected_response_time", 0),
                    auth=request.get("auth", None),
                )
                request_config.append(config)
        return request_config

    def read_configs(self):
        """
        Read and parse all configuration files.

        This method:
        1. Reads the main test configuration file
        2. Reads the request configurations file if specified
        3. Validates required fields and structure
        4. Creates phase, scenario, and request configurations
        5. Handles ramp-up and timing configurations

        Raises:
            AssertionError: If required fields are missing or invalid
        """
        info("Reading configs...")

        with open(self.test_config_file_path, "r") as scenario_file:
            scenarios_config = yaml.safe_load(scenario_file)

        if self.request_configs_path:
            with open(self.request_configs_path, "r") as param_file:
                params_config = yaml.safe_load(param_file)

        else:
            params_config = {}

        self.phases = []

        assert_not_empty("run_name", scenarios_config["runs"]["name"])
        self.run_name = scenarios_config["runs"]["name"]
        self.phase_wait = scenarios_config["runs"].get("wait_between_phases", 0)

        assert_not_empty("phases", scenarios_config["runs"].get("phases"))

        for phase_name, phase_data in scenarios_config["runs"]["phases"].items():
            scenarios = []

            assert_not_empty(
                f"scenarios for phase: {phase_name}",
                phase_data.get("scenarios"),
            )

            for scenario_name, scenario_data in phase_data["scenarios"].items():
                request_configs = []

                if scenario_data["requests"] == "FROM_REQUEST_YAML_FILE":
                    request_configs = self.read_request_file(
                        scenario_data["request_file"]
                    )
                else:
                    for scenario_request_name in scenario_data["requests"]:
                        request = params_config["requests"][scenario_request_name]
                        request_configs.append(
                            RequestConfig(
                                name=scenario_request_name,
                                url=request.get("url", ""),
                                params=request.get("params", {}),
                                http_method=request.get("method", "get"),
                                expected_response_time=request[
                                    "expected_response_time"
                                ],
                                auth=request.get("auth", None),
                            )
                        )
                ramp_up = []
                ramp_up_wait = []
                ramp_up_multiply = scenario_data.get("ramp_up_multiply", None)
                if ramp_up_multiply:
                    ramp_up = convert_list(ramp_up_multiply)
                    multiply = True
                else:
                    ramp_up = convert_list(scenario_data.get("ramp_up_add", 0))
                    multiply = False

                ramp_up_wait = convert_list(scenario_data.get("ramp_up_wait", [0.1]))
                run_once = scenario_data.get("run_once", False)
                iterate_through_requests = scenario_data.get(
                    "iterate_through_requests", False
                )
                scenarios.append(
                    ScenarioConfig(
                        name=scenario_name,
                        min_concurrency=validate_min_concurrency(
                            scenario_data["min_concurrency"], multiply
                        ),
                        max_concurrency=scenario_data["max_concurrency"],
                        ramp_up=ramp_up,
                        ramp_up_wait=ramp_up_wait,
                        request_configs=request_configs,
                        multiply=multiply,
                        run_once=run_once,
                        iterate_through_requests=iterate_through_requests,
                    )
                )
            self.phases.append(
                PhaseConfig(
                    name=phase_name,
                    scenario_config=scenarios,
                    runtime=phase_data["run_time"],
                )
            )
