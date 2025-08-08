import pytest
from unittest.mock import Mock, patch
import gevent
from gradual.runners.phase import Phase
from gradual.configs.phase import PhaseConfig


@pytest.fixture
def mock_phase_config():
    config = Mock(spec=PhaseConfig)
    config.name = "test_phase"
    config.phase_runtime = 5
    # Provide a list of mocks with the right spec and attributes
    mock_cat_config = Mock()
    mock_cat_config.iterate_through_requests = False
    mock_cat_config.min_concurrency = 1
    mock_cat_config.max_concurrency = 1
    mock_cat_config.ramp_up = [1]
    mock_cat_config.ramp_up_wait = [0.1]
    mock_cat_config.multiply = False
    mock_cat_config.run_once = False
    mock_cat_config.request_configs = []
    config.scenario_config = [mock_cat_config]
    return config


def test_phase_initialization(mock_phase_config):
    """Test that Phase initializes correctly with config and run name."""
    with (
        patch("gradual.runners.phase.Stats") as mock_stats,
        patch("gradual.runners.phase.Runner") as mock_runner,
    ):
        phase = Phase(mock_phase_config, "test_run")
        mock_stats.assert_called_once_with(mock_phase_config, "test_run")
        mock_runner.assert_called_once_with(mock_phase_config.scenario_config)
        assert phase.phase_config == mock_phase_config
        assert phase.reporting_object == mock_stats.return_value
        assert phase.runner == mock_runner.return_value


def test_phase_execution(mock_phase_config):
    """Test normal phase execution without timeout."""
    with (
        patch("gradual.runners.phase.Stats"),
        patch("gradual.runners.phase.Runner") as mock_runner,
    ):
        phase = Phase(mock_phase_config, "test_run")
        phase.runner.start_test = Mock()
        with (
            patch("gevent.spawn") as mock_spawn,
            patch("gevent.wait") as mock_wait,
            patch("gevent.Timeout") as mock_timeout,
        ):
            mock_task = Mock()
            mock_spawn.return_value = mock_task
            phase.execute()
            mock_spawn.assert_called_once_with(phase.runner.start_test)
            mock_wait.assert_called_once_with(objects=[mock_task])
            args, kwargs = mock_timeout.call_args
            assert args[0] == mock_phase_config.phase_runtime
            assert isinstance(args[1], TimeoutError)
            assert str(args[1]) == "Phase exceeded runtime."


def test_phase_timeout(mock_phase_config):
    """Test phase execution with timeout."""
    with (
        patch("gradual.runners.phase.Stats"),
        patch("gradual.runners.phase.Runner") as mock_runner,
    ):
        phase = Phase(mock_phase_config, "test_run")
        phase.runner.stop_runner = Mock()
        with (
            patch("gevent.spawn") as mock_spawn,
            patch("gevent.wait", side_effect=TimeoutError()),
            patch("gevent.Timeout") as mock_timeout,
        ):
            mock_task = Mock()
            mock_spawn.return_value = mock_task
            phase.execute()
            phase.runner.stop_runner.assert_called_once()


def test_stop_phase(mock_phase_config):
    """Test stopping a phase."""
    with (
        patch("gradual.runners.phase.Stats"),
        patch("gradual.runners.phase.Runner") as mock_runner,
    ):
        phase = Phase(mock_phase_config, "test_run")
        phase.runner.stop_runner = Mock()
        phase.stop_phase()
        phase.runner.stop_runner.assert_called_once()


def test_phase_execution_error_handling(mock_phase_config):
    """Test error handling during phase execution."""
    with (
        patch("gradual.runners.phase.Stats"),
        patch("gradual.runners.phase.Runner") as mock_runner,
    ):
        phase = Phase(mock_phase_config, "test_run")
        phase.runner.stop_runner = Mock()
        with (
            patch("gevent.spawn") as mock_spawn,
            patch("gevent.wait", side_effect=Exception("Test error")),
            patch("gevent.Timeout") as mock_timeout,
        ):
            mock_task = Mock()
            mock_spawn.return_value = mock_task
            with pytest.raises(Exception) as exc_info:
                phase.execute()
            assert str(exc_info.value) == "Test error"
            phase.runner.stop_runner.assert_called_once()


def test_phase_runtime_validation(mock_phase_config):
    """Test that phase runtime is properly validated."""
    mock_phase_config.phase_runtime = -1
    with pytest.raises(ValueError):
        Phase(mock_phase_config, "test_run")


def test_phase_name_validation(mock_phase_config):
    """Test that phase name is properly validated."""
    mock_phase_config.name = ""
    with pytest.raises(ValueError):
        Phase(mock_phase_config, "test_run")
