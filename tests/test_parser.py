import pytest
from unittest.mock import patch, mock_open
from gradual.configs.parser import Parser
from gradual.configs.phase import PhaseConfig
from gradual.configs.scenario import ScenarioConfig
from gradual.configs.request import RequestConfig

# filepath: src/gradual/configs/test_parser.py


@pytest.fixture
def mock_yaml_data():
    return {
        "runs": {
            "name": "test_run",
            "wait_between_phases": 2,
            "phases": {
                "phase1": {
                    "scenarios": {
                        "scenario1": {
                            "min_concurrency": 1,
                            "max_concurrency": 10,
                            "ramp_up_add": [1, 2],
                            "ramp_up_wait": [0.1, 0.2],
                            "requests": ["request1", "request2"],
                        }
                    },
                    "run_time": 60,
                }
            },
        }
    }


@pytest.fixture
def mock_request_yaml_data():
    return {
        "requests": {
            "request1": {
                "url": "http://example.com",
                "params": {"key": "value"},
                "method": "get",
                "expected_response_time": 200,
            },
            "request2": {
                "url": "http://example2.com",
                "params": {"key2": "value2"},
                "method": "post",
                "expected_response_time": 300,
            },
        }
    }


@patch("builtins.open", new_callable=mock_open)
@patch("yaml.safe_load")
@patch("gradual.configs.parser.assert_not_empty")
def test_read_configs(
    mock_assert_not_empty,
    mock_yaml_safe_load,
    mock_open_file,
    mock_yaml_data,
    mock_request_yaml_data,
):
    # Mock YAML data for test_config_file_path
    mock_yaml_safe_load.side_effect = [mock_yaml_data, mock_request_yaml_data]

    parser = Parser("test_config_path.yaml", "request_configs_path.yaml")
    parser.read_configs()

    # Assertions for run_name and phase_wait
    assert parser.run_name == "test_run"
    assert parser.phase_wait == 2

    # Assertions for phases
    assert len(parser.phases) == 1
    phase = parser.phases[0]
    assert isinstance(phase, PhaseConfig)
    assert phase.name == "phase1"
    assert len(phase.scenario_config) == 1

    # Assertions for scenario_config
    scenario = phase.scenario_config[0]
    assert isinstance(scenario, ScenarioConfig)
    assert scenario.name == "scenario1"
    assert scenario.min_concurrency == 1
    assert scenario.max_concurrency == 10
    assert scenario.ramp_up == [1, 2]
    assert scenario.ramp_up_wait == [0.1, 0.2]
    assert len(scenario.request_configs) == 2

    # Assertions for request_configs
    request1 = scenario.request_configs[0]
    assert isinstance(request1, RequestConfig)
    assert request1.name == "request1"
    assert request1.url == "http://example.com"
    assert request1.params == {"key": "value"}
    assert request1.http_method == "get"
    assert request1.expected_response_time == 200

    request2 = scenario.request_configs[1]
    assert isinstance(request2, RequestConfig)
    assert request2.name == "request2"
    assert request2.url == "http://example2.com"
    assert request2.params == {"key2": "value2"}
    assert request2.http_method == "post"
    assert request2.expected_response_time == 300

    # Verify assert_not_empty requests
    assert mock_assert_not_empty.call_count > 0


@patch("builtins.open", new_callable=mock_open)
@patch("yaml.safe_load")
@patch("gradual.configs.parser.assert_not_empty")
def test_parser_multiple_phases_and_scenarios(
    mock_assert_not_empty, mock_yaml_safe_load, mock_open_file
):
    # Mock YAML data for multiple phases and scenarios
    mock_yaml_data = {
        "runs": {
            "name": "multi_run",
            "wait_between_phases": 1,
            "phases": {
                "phase1": {
                    "scenarios": {
                        "scenario1": {
                            "min_concurrency": 1,
                            "max_concurrency": 5,
                            "ramp_up_add": [1],
                            "ramp_up_wait": [0.1],
                            "requests": ["request1"],
                        },
                        "scenario2": {
                            "min_concurrency": 2,
                            "max_concurrency": 10,
                            "ramp_up_add": [2, 3],
                            "ramp_up_wait": [0.2, 0.3],
                            "requests": ["request2"],
                        },
                    },
                    "run_time": 30,
                },
                "phase2": {
                    "scenarios": {
                        "scenario3": {
                            "min_concurrency": 3,
                            "max_concurrency": 15,
                            "ramp_up_add": [4],
                            "ramp_up_wait": [0.4],
                            "requests": ["request3"],
                        }
                    },
                    "run_time": 40,
                },
            },
        }
    }
    mock_request_yaml_data = {
        "requests": {
            "request1": {
                "url": "http://a.com",
                "params": {},
                "method": "get",
                "expected_response_time": 100,
            },
            "request2": {
                "url": "http://b.com",
                "params": {},
                "method": "post",
                "expected_response_time": 200,
            },
            "request3": {
                "url": "http://c.com",
                "params": {},
                "method": "put",
                "expected_response_time": 300,
            },
        }
    }
    mock_yaml_safe_load.side_effect = [mock_yaml_data, mock_request_yaml_data]
    parser = Parser("test_config_path.yaml", "request_configs_path.yaml")
    parser.read_configs()
    assert parser.run_name == "multi_run"
    assert parser.phase_wait == 1
    assert len(parser.phases) == 2
    phase_names = {s.name for s in parser.phases}
    assert phase_names == {"phase1", "phase2"}
    # Check scenarios in phase1
    phase1 = next(s for s in parser.phases if s.name == "phase1")
    assert len(phase1.scenario_config) == 2
    scenario_names = {c.name for c in phase1.scenario_config}
    assert scenario_names == {"scenario1", "scenario2"}
    # Check scenarios in phase2
    phase2 = next(s for s in parser.phases if s.name == "phase2")
    assert len(phase2.scenario_config) == 1
    assert phase2.scenario_config[0].name == "scenario3"
    # Check all scenarios and calls
    for scenario in phase1.scenario_config:
        for request in scenario.request_configs:
            assert request.url.startswith("http://")


@patch("builtins.open", new_callable=mock_open)
@patch("yaml.safe_load")
@patch("gradual.configs.parser.assert_not_empty")
def test_parser_missing_required_fields_raises(
    mock_assert_not_empty, mock_yaml_safe_load, mock_open_file
):
    # Missing 'runs' key
    mock_yaml_safe_load.side_effect = [{}, {}]
    parser = Parser("test_config_path.yaml", "request_configs_path.yaml")
    with pytest.raises(Exception):
        parser.read_configs()


@patch("builtins.open", new_callable=mock_open)
@patch("yaml.safe_load")
@patch("gradual.configs.parser.assert_not_empty")
def test_parser_invalid_ramp_up_type_raises(
    mock_assert_not_empty, mock_yaml_safe_load, mock_open_file
):
    # ramp_up_add is a string instead of a list
    mock_yaml_data = {
        "runs": {
            "name": "test_run",
            "wait_between_phases": 2,
            "phases": {
                "phase1": {
                    "scenarios": {
                        "scenario1": {
                            "min_concurrency": 1,
                            "max_concurrency": 10,
                            "ramp_up_add": "not_a_list",
                            "ramp_up_wait": [0.1],
                            "requests": ["request1"],
                        }
                    },
                    "run_time": 60,
                }
            },
        }
    }
    mock_request_yaml_data = {
        "requests": {
            "request1": {
                "url": "http://example.com",
                "params": {},
                "method": "get",
                "expected_response_time": 100,
            },
        }
    }
    mock_yaml_safe_load.side_effect = [mock_yaml_data, mock_request_yaml_data]
    parser = Parser("test_config_path.yaml", "request_configs_path.yaml")
    with pytest.raises(Exception):
        parser.read_configs()


@patch("builtins.open", new_callable=mock_open)
@patch("yaml.safe_load")
@patch("gradual.configs.parser.assert_not_empty")
def test_parser_optional_fields(
    mock_assert_not_empty, mock_yaml_safe_load, mock_open_file
):
    mock_yaml_data = {
        "runs": {
            "name": "test_run",
            "wait_between_phases": 2,
            "phases": {
                "phase1": {
                    "scenarios": {
                        "scenario1": {
                            "min_concurrency": 1,
                            "max_concurrency": 10,
                            "ramp_up_multiply": [2, 3],
                            "ramp_up_wait": [0.1, 0.2],
                            "requests": ["request1"],
                            "run_once": True,
                            "iterate_through_requests": True,
                        },
                        "scenario2": {
                            "min_concurrency": 2,
                            "max_concurrency": 5,
                            "ramp_up_add": [1],
                            "ramp_up_wait": [0.1],
                            "requests": ["request2"],
                            # run_once and iterate_through_requests omitted
                        },
                    },
                    "run_time": 60,
                }
            },
        }
    }
    mock_request_yaml_data = {
        "requests": {
            "request1": {
                "url": "http://example.com",
                "params": {"key": "value"},
                "method": "get",
                "expected_response_time": 200,
            },
            "request2": {
                "url": "http://example2.com",
                "params": {"key2": "value2"},
                "method": "post",
                "expected_response_time": 300,
            },
        }
    }
    mock_yaml_safe_load.side_effect = [mock_yaml_data, mock_request_yaml_data]
    parser = Parser("test_config_path.yaml", "request_configs_path.yaml")
    parser.read_configs()
    scenarios = parser.phases[0].scenario_config
    scenario1 = next(c for c in scenarios if c.name == "scenario1")
    scenario2 = next(c for c in scenarios if c.name == "scenario2")
    # scenario1: all optional fields present
    assert scenario1.multiply is True
    assert scenario1.ramp_up == [2, 3]
    assert scenario1.run_once is True
    assert scenario1.iterate_through_requests is True
    # scenario2: optional fields omitted, should use defaults
    assert scenario2.multiply is False
    assert scenario2.ramp_up == [1]
    assert scenario2.run_once is False
    assert scenario2.iterate_through_requests is False
