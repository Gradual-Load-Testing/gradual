import pytest
from unittest.mock import Mock, patch
import gevent
from gradual.runners.runner import Runner
from gradual.configs.scenario import ScenarioConfig


@pytest.fixture
def mock_scenario_configs():
    """Create mock scenario configs for testing."""
    configs = []
    for i in range(2):
        # Create a mock request config
        mock_request_config = Mock()
        mock_request_config.name = f"test_request_{i+1}"
        mock_request_config.params = {}
        mock_request_config.http_method = "GET"
        mock_request_config.expected_response_time = 1.0
        mock_request_config.url = None
        mock_request_config.type = None

        # Create the scenario config
        config = Mock(spec=ScenarioConfig)
        config.name = f"scenario{i+1}"
        config.iterate_through_requests = False
        config.min_concurrency = 1
        config.max_concurrency = 5
        config.ramp_up = [2, 3, 4]
        config.ramp_up_wait = [0.1]
        config.multiply = False
        config.run_once = False
        config.request_configs = [mock_request_config]
        configs.append(config)
    return configs


@pytest.fixture
def runner(mock_scenario_configs):
    with patch("gradual.runners.runner.Scenario") as mock_scenario:
        mock_scenario.return_value = Mock()
        runner = Runner(mock_scenario_configs)
        return runner


def test_runner_initialization(mock_scenario_configs):
    """Test that Runner initializes correctly with scenario configs."""
    with patch("gradual.runners.runner.Scenario") as mock_scenario:
        mock_scenario.return_value = Mock()
        runner = Runner(mock_scenario_configs)

        assert len(runner.scenarios) == len(mock_scenario_configs)
        assert len(runner.running_scenarios) == 0
        assert len(runner.running_scenarios_task) == 0


def test_start_test(runner, mock_scenario_configs):
    """Test starting test execution for all scenarios."""
    with patch("gevent.spawn") as mock_spawn, patch("gevent.wait") as mock_wait:

        mock_task = Mock()
        mock_spawn.return_value = mock_task

        runner.start_test()

        # Verify each scenario was started
        assert len(runner.running_scenarios) == len(mock_scenario_configs)
        assert len(runner.running_scenarios_task) == len(mock_scenario_configs)
        assert mock_spawn.call_count == len(mock_scenario_configs)
        mock_wait.assert_called_once_with(runner.running_scenarios_task)
        runner.stop_runner()


def test_stop_runner(runner, mock_scenario_configs):
    """Test stopping all running scenarios."""
    # First start the test to populate running scenarios
    with patch("gevent.spawn") as mock_spawn, patch("gevent.wait") as mock_wait:

        mock_task = Mock()
        mock_spawn.return_value = mock_task
        runner.start_test()

    # Now test stopping
    with patch("gevent.wait") as mock_wait:  # Mock wait to prevent LoopExit
        runner.stop_runner()

    # Verify all scenarios were stopped
    for scenario in runner.running_scenarios:
        assert scenario.stop_scenario_execution is True


def test_runner_error_handling(runner, mock_scenario_configs):
    """Test error handling during test execution."""
    with (
        patch("gevent.spawn") as mock_spawn,
        patch("gevent.wait", side_effect=Exception("Test error")),
    ):

        mock_task = Mock()
        mock_spawn.return_value = mock_task

        with pytest.raises(Exception) as exc_info:
            runner.start_test()

        assert str(exc_info.value) == "Test error"


def test_runner_empty_scenarios():
    """Test runner behavior with empty scenario list."""
    runner = Runner([])

    assert len(runner.scenarios) == 0
    assert len(runner.running_scenarios) == 0
    assert len(runner.running_scenarios_task) == 0


def test_runner_scenario_execution_order(runner, mock_scenario_configs):
    """Test that scenarios are executed in the correct order."""
    execution_order = []

    def mock_execute():
        execution_order.append(len(execution_order) + 1)

    # Mock the request class to prevent NotImplementedError
    class MockRequest:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            pass

    # Mock the iterator class
    class MockIterator:
        def __init__(self, *args, **kwargs):
            pass

        def get_next_request(self):
            return Mock()

    with (
        patch("gevent.spawn") as mock_spawn,
        patch("gevent.wait") as mock_wait,
        patch("gradual.runners.runner.Scenario") as mock_scenario,
        patch("gradual.runners.scenario._Request", MockRequest),
        patch("gradual.runners.scenario.RequestIterator", MockIterator),
    ):
        # Create a new mock for each scenario
        mock_instances = []
        for _ in mock_scenario_configs:
            mock_instance = Mock()
            mock_instance.execute.side_effect = mock_execute
            mock_instances.append(mock_instance)

        mock_scenario.side_effect = mock_instances

        # Set up spawn to actually requests the execute function
        def spawn_side_effect(func):
            func()
            return Mock()

        mock_spawn.side_effect = spawn_side_effect

        runner = Runner(mock_scenario_configs)
        runner.start_test()

        # Verify scenarios were executed in order
        assert execution_order == [1, 2]
        runner.stop_runner()


def test_runner_stop_before_start():
    """Test stopping runner before starting any tests."""
    runner = Runner([])
    runner.stop_runner()  # Should not raise any errors

    assert len(runner.running_scenarios) == 0
    assert len(runner.running_scenarios_task) == 0
