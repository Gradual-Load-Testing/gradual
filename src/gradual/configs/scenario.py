"""
The scenario module provides the ScenarioConfig class which defines the configuration
for a group of related API requests in stress testing. It manages concurrency, ramp-up
behavior, and request iteration settings.
"""

from dataclasses import asdict, dataclass

from gradual.configs.request import RequestConfig


@dataclass
class ScenarioConfig:
    """
    Configuration class for a scenario of API requests in stress testing.

    This class defines how a group of related API requests should be executed,
    including concurrency settings, ramp-up behavior, and request iteration patterns.

    Attributes:
        name (str): Unique identifier for this scenario
        min_concurrency (int): Minimum number of concurrent requests
        max_concurrency (int): Maximum number of concurrent requests
        ramp_up (list[int]): List of values for gradual increase in concurrency
        ramp_up_wait (list[int]): List of wait times between ramp-up steps
        request_configs (list[RequestConfig]): List of request configurations in this scenario
        multiply (bool): Whether to multiply or add during ramp-up
        run_once (bool): Whether requests should run only once
        iterate_through_requests (bool): Whether to cycle through all requests
    """

    name: str
    min_concurrency: int
    max_concurrency: int
    ramp_up: list[int]
    ramp_up_wait: list[int]
    request_configs: list[RequestConfig]
    multiply: bool
    run_once: bool
    iterate_through_requests: bool

    def as_simple_obj(self):
        """
        Convert the scenario configuration to a simplified dictionary format.

        This method transforms the configuration into a more compact representation
        suitable for reporting or serialization. It:
        1. Converts the configuration to a dictionary
        2. Replaces request_configs with a count
        3. Renames ramp_up based on multiply setting
        4. Restructures the output with scenario name as key

        Returns:
            dict: Simplified configuration object with scenario name as key
        """
        obj_dict = asdict(self)
        obj_dict["no_of_requests"] = len(obj_dict.pop("request_configs"))
        if self.multiply:
            obj_dict["ramp_up_multiply"] = obj_dict.pop("ramp_up", None)
        else:
            obj_dict["ramp_up_add"] = obj_dict.pop("ramp_up", None)

        obj_dict.pop("name")
        obj_dict = {self.name: obj_dict}
        return obj_dict
