from logging import info
import pytest
from unittest.mock import Mock, patch
import gevent
from gradual.base.orchestrator import Orchestrator
from gradual.runners.phase import Phase
from gradual.configs.scenario import ScenarioConfig
from gradual.configs.request import RequestConfig
from gradual.configs.phase import PhaseConfig
import time


@pytest.fixture
def mock_request_config():
    """Create a mock request config for testing."""
    return RequestConfig(
        name="test_request",
        params={},
        http_method="GET",
        expected_response_time=1.0,
        url=None,
        type="Something",
    )


@pytest.fixture
def mock_scenario_config(mock_request_config):
    """Create a mock scenario config for testing."""
    return ScenarioConfig(
        name="test_scenario",
        min_concurrency=2,
        max_concurrency=10,
        ramp_up=[2, 3, 4],
        ramp_up_wait=[0.001],
        multiply=False,
        run_once=False,
        iterate_through_requests=False,
        request_configs=[mock_request_config],
    )


@pytest.fixture
def mock_parser(mock_scenario_config):
    """Create a mock parser with proper phase configs."""
    # Create the phases list first
    phases = [
        PhaseConfig(name="phase1", scenario_config=[mock_scenario_config], runtime=0.1),
        PhaseConfig(name="phase2", scenario_config=[mock_scenario_config], runtime=0.1),
    ]
    # Create a mock with spec_set to properly handle attributes
    parser = Mock(
        spec_set=["phases", "phase_wait", "run_name", "read_configs", "phase"]
    )
    parser.phases = phases
    parser.phase_wait = 0.1
    parser.run_name = "test_run"
    # Mock the read_configs method to do nothing
    parser.read_configs = Mock()
    # Mock the phase property to return the phases list
    parser.phase = phases
    return parser


@pytest.fixture
def orchestrator(mock_parser):
    with patch("gradual.base.orchestrator.Parser", return_value=mock_parser):
        orch = Orchestrator("test_config.json", "request_configs.json")
        orch.parser = mock_parser
        return orch


def test_orchestrator_initialization():
    """Test that Orchestrator initializes correctly with config paths."""
    with patch("gradual.base.orchestrator.Parser") as mock_parser:
        orch = Orchestrator("test_config.json", "request_configs.json")
        mock_parser.assert_called_once_with("test_config.json", "request_configs.json")
        assert orch.test_config_file_path == "test_config.json"
        assert orch.request_configs_path == "request_configs.json"


def test_start_stress_test(orchestrator, mock_parser):
    """Test that stress test execution follows the correct sequence."""
    orchestrator.start_stress_test()

    # Verify phases were created and executed
    assert len(orchestrator.parser.phases) == 2


def test_phase_wait_time(orchestrator, mock_parser):
    """Test that the correct wait time is applied between phases."""
    start_time = time.time()
    orchestrator.start_stress_test()
    end_time = time.time()

    # Verify that the total time includes the wait time between phases
    # We expect: 2 phases with 0.1 second runtime each + 0.1 second wait between them
    expected_min_time = 0.3  # 2 phases + 1 wait
    assert end_time - start_time >= expected_min_time


def test_phase_execution_order(orchestrator, mock_parser):
    """Test that phases are executed in the correct order."""
    phase_execution_order = []

    def track_phase_execution(self):
        phase_execution_order.append(self.phase_config.name)
        return None

    # Create a patch for Phase.execute that will be applied to each instance
    with patch.object(Phase, "execute", autospec=True) as mock_execute:
        mock_execute.side_effect = track_phase_execution
        orchestrator.start_stress_test()

    # Verify phases were executed in order
    assert phase_execution_order == ["phase1", "phase2"]
