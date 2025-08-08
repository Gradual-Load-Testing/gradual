import pytest
import gevent
from gradual.configs.scenario import ScenarioConfig
from gradual.configs.request import RequestConfig
from gradual.constants.request_types import RequestType
from gradual.runners.iterators import RequestIterator
from gradual.runners.scenario import Scenario
from gradual.runners.request.base import _Request
from gradual.runners.request.Http import HttpRequest
from gradual.runners.request.SocketIO import SocketRequest


@pytest.fixture
def scenario_config():
    """Create a basic scenario config for testing."""
    # Create request config with invalid type to trigger implementation error
    request_config = RequestConfig(
        name="somerequest",
        params={},
        http_method="GET",
        expected_response_time=1.0,
        url=None,
        type="Something",
    )

    return ScenarioConfig(
        name="test_scenario",
        min_concurrency=2,
        max_concurrency=10,
        ramp_up=[2, 3, 4],
        ramp_up_wait=[0.001],  # 1ms wait
        multiply=False,
        run_once=False,
        iterate_through_requests=False,
        request_configs=[request_config],
    )


def test_do_ramp_up(scenario_config):
    """Test ramp up with requests."""
    scenario = Scenario(scenario_config)

    scenario.do_ramp_up(2)

    # Wait for tasks to complete
    gevent.wait(scenario.running_request_tasks)

    # Check that all tasks failed with NotImplementedError
    for task in scenario.running_request_tasks:
        assert isinstance(task.exception, NotImplementedError)
        assert str(task.exception) == "Expected subclasses to implement this method."

    # Verify the requests were made correctly
    assert len(scenario.running_request_tasks) == 2
    assert len(scenario.requests) == 2
    assert all(isinstance(request, _Request) for request in scenario.requests)
    assert not any(
        isinstance(request, (HttpRequest, SocketRequest))
        for request in scenario.requests
    )


def test_do_ramp_up_max_concurrency(scenario_config):
    """Test ramp up respects max concurrency limit."""
    scenario_config.max_concurrency = 3

    scenario = Scenario(scenario_config)

    scenario.do_ramp_up(5)  # Try to ramp up more than max_concurrency

    # Wait for tasks to complete
    gevent.wait(scenario.running_request_tasks)

    assert len(scenario.running_request_tasks) <= scenario_config.max_concurrency


def test_do_ramp_up_with_iteration(scenario_config):
    """Test ramp up when iterate_through_requests is True."""
    scenario_config.iterate_through_requests = True

    scenario = Scenario(scenario_config)

    scenario.do_ramp_up(2)

    # Wait for tasks to complete
    gevent.wait(scenario.running_request_tasks)

    assert len(scenario.running_request_tasks) == 2
    assert len(scenario.requests) == 2


def test_do_ramp_up_with_multiple_requests(scenario_config):
    """Test ramp up with multiple request configs to verify iterator behavior."""
    # Create multiple request configs
    request_configs = [
        RequestConfig(
            name="request1",
            params={},
            http_method="GET",
            expected_response_time=1.0,
            url=None,
            type="Something",
        ),
        RequestConfig(
            name="request2",
            params={},
            http_method="GET",
            expected_response_time=1.0,
            url=None,
            type="Something",
        ),
        RequestConfig(
            name="request3",
            params={},
            http_method="GET",
            expected_response_time=1.0,
            url=None,
            type="Something",
        ),
    ]

    # Update scenario config with multiple requests
    scenario_config.request_configs = request_configs
    scenario_config.iterate_through_requests = True

    scenario = Scenario(scenario_config)

    # Ramp up to create more requests than we have request configs
    scenario.do_ramp_up(5)

    # Wait for tasks to complete
    gevent.wait(scenario.running_request_tasks)

    # Check that all tasks failed with NotImplementedError
    for task in scenario.running_request_tasks:
        assert isinstance(task.exception, NotImplementedError)
        assert str(task.exception) == "Expected subclasses to implement this method."

    # Verify the requests were made correctly
    assert len(scenario.running_request_tasks) == 5
    assert len(scenario.requests) == 5

    # Verify that requests were created in the correct order
    # The first 3 requests should match our request configs in order
    for i in range(3):
        assert scenario.requests[i].iterator.get_next_request().name == f"request{i+1}"

    # The last 2 requests should cycle back to the beginning
    assert scenario.requests[3].iterator.get_next_request().name == "request1"
    assert scenario.requests[4].iterator.get_next_request().name == "request2"

    # Verify all requests are base _Request instances
    assert all(isinstance(request, _Request) for request in scenario.requests)
    assert not any(
        isinstance(request, (HttpRequest, SocketRequest))
        for request in scenario.requests
    )


def test_do_ramp_up_with_multiple_requests_no_iteration(scenario_config):
    """Test ramp up with multiple request configs when iterate_through_requests is False."""
    # Create multiple request configs
    request_configs = [
        RequestConfig(
            name="request1",
            params={},
            http_method="GET",
            expected_response_time=1.0,
            url=None,
            type="Something",
        ),
        RequestConfig(
            name="request2",
            params={},
            http_method="GET",
            expected_response_time=1.0,
            url=None,
            type="Something",
        ),
        RequestConfig(
            name="request3",
            params={},
            http_method="GET",
            expected_response_time=1.0,
            url=None,
            type="Something",
        ),
    ]

    # Update scenario config with multiple requests
    scenario_config.request_configs = request_configs
    scenario_config.iterate_through_requests = False

    scenario = Scenario(scenario_config)

    # Ramp up to create more requests than we have request configs
    scenario.do_ramp_up(5)

    # Wait for tasks to complete
    gevent.wait(scenario.running_request_tasks)

    # Check that all tasks failed with NotImplementedError
    for task in scenario.running_request_tasks:
        assert isinstance(task.exception, NotImplementedError)
        assert str(task.exception) == "Expected subclasses to implement this method."

    # Verify the requests were made correctly
    assert len(scenario.running_request_tasks) == 5
    assert len(scenario.requests) == 5

    # Verify that each request has its own iterator with a single request config
    # The first 3 requests should match our request configs in order
    for i in range(3):
        assert len(scenario.requests[i].iterator.request_types) == 1
        assert scenario.requests[i].iterator.request_types[0].name == f"request{i+1}"

    # The last 2 requests should cycle back to the beginning
    assert len(scenario.requests[3].iterator.request_types) == 1
    assert scenario.requests[3].iterator.request_types[0].name == "request1"
    assert len(scenario.requests[4].iterator.request_types) == 1
    assert scenario.requests[4].iterator.request_types[0].name == "request2"

    # Verify all requests are base _Request instances
    assert all(isinstance(request, _Request) for request in scenario.requests)
    assert not any(
        isinstance(request, (HttpRequest, SocketRequest))
        for request in scenario.requests
    )
