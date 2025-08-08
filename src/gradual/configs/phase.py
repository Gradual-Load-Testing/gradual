"""
The phase module provides the PhaseConfig class which defines the configuration
for a test phase in stress testing. A phase represents a self-contained unit
of testing with its own runtime and scenario configurations.
"""

from dataclasses import asdict, dataclass

from gradual.configs.scenario import ScenarioConfig


@dataclass
class PhaseConfig:
    """
    Configuration class for a test phase in stress testing.

    This class defines a self-contained unit of testing that includes:
    1. A set of scenario configurations to execute
    2. A runtime limit for the entire phase
    3. Methods for serialization and reporting

    Attributes:
        name (str): Unique identifier for this phase
        scenario_config (list[ScenarioConfig]): List of scenario configurations to execute
        runtime (int): Maximum runtime for this phase in seconds
    """

    name: str
    scenario_config: list[ScenarioConfig]
    runtime: int

    @property
    def phase_runtime(self):
        """
        Get the runtime limit for this phase.

        Returns:
            int: Maximum runtime for this phase in seconds
        """
        return self.runtime

    def as_simple_obj(self):
        """
        Convert the phase configuration to a simplified dictionary format.

        This method transforms the configuration into a more compact representation
        suitable for reporting or serialization. It:
        1. Converts the configuration to a dictionary
        2. Converts each scenario configuration to its simplified form

        Returns:
            dict: Simplified configuration object with all nested configurations
        """
        obj_dict = asdict(self)
        obj_dict["scenario_config"] = [
            scenario.as_simple_obj() for scenario in self.scenario_config
        ]
        return obj_dict
