# Configuration Reference

This document provides a comprehensive reference for all configuration options available in Gradual. It's designed to be your go-to resource for understanding, configuring, and troubleshooting Gradual stress tests.

> **💡 This is the dedicated Configuration Reference guide. For a quick overview, see the [User Guide](user_guide.md).**

## Overview

Gradual uses a two-file configuration system:

1. **Test Configuration** (`test_config.yaml`) - Defines the overall test structure, phases, and scenarios
2. **Request Configuration** (`request_config.yaml`) - Defines individual HTTP requests and their parameters

## Command-Line Usage

The `stress-run` command is the main entry point for running stress tests. It accepts the following arguments:

```bash
stress-run --test_config <test_config_file> [--request_config <request_config_file>]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--test_config` | path | Yes | Path to the main test configuration file (YAML) |
| `--request_config` | path | No | Path to the request configuration file (YAML). If not provided, requests must be defined inline in the test configuration. |

### Examples

```bash
# Run with both configuration files
stress-run --test_config test_config.yaml --request_config request_config.yaml

# Run with only test configuration (requests defined inline)
stress-run --test_config test_config.yaml

# Run with relative paths
stress-run --test_config ./configs/test.yaml --request_config ./configs/requests.yaml
```

### Dashboard Command

The `stress-dashboard` command provides real-time monitoring:

```bash
# Start Bokeh dashboard (interactive charts)
stress-dashboard --mode bokeh --port 8080

# Start WebSocket dashboard (lightweight)
stress-dashboard --mode websocket --port 8081

# Start with custom host
stress-dashboard --mode bokeh --host 0.0.0.0 --port 8080
```

> **⚠️ Important:** The CLI does not support command-line overrides for configuration values. All test parameters must be defined in the YAML configuration files.

### CLI Implementation Details

The current CLI implementation is intentionally simple and focused:

- **No command-line overrides**: All test parameters (concurrency, duration, ramp-up, etc.) must be defined in YAML files
- **No output format options**: Results are displayed in the console by default
- **No debug flags**: Logging level is controlled by the configuration files
- **No report generation**: Use the dashboard for real-time monitoring and analysis

This design ensures that:
- Tests are reproducible and version-controlled
- Configuration is explicit and documented
- Test behavior is consistent across different environments
- Users focus on proper test design rather than command-line tweaking

### CLI Source Code

The CLI is implemented in `scripts/run_stress_test.py` and provides a minimal interface:

```python
parser = ArgumentParser()
parser.add_argument(
    "--test_config",
    type=pathlib.Path,
    required=True,
    help="Path to the test configuration file",
)
parser.add_argument(
    "--request_config", 
    type=pathlib.Path, 
    help="Path to the request configuration file"
)
```

This simplicity allows for:
- Easy integration with CI/CD pipelines
- Consistent behavior across different environments
- Clear separation of concerns between CLI and configuration
- Focus on test design rather than command-line complexity

## Test Configuration File

The test configuration file is the main configuration file that defines how your stress test will be executed.

### Top-Level Structure

```yaml
runs:
  name: "Test Run Name"
  wait_between_phases: 10
  phases:
    "phase_name":
      # Phase configuration
```

### Run Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Name of the test run |
| `wait_between_phases` | integer | No | Wait time between phases in seconds (default: 0) |

### Phase Configuration

Each phase represents a distinct period of testing with specific load characteristics.

```yaml
"phase_name":
  scenarios:
    "scenario_name":
      # Scenario configuration
  run_time: 300
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scenarios` | object | Yes | Dictionary of scenarios to run in this phase |
| `run_time` | integer | Yes | Duration of the phase in seconds |

### Scenario Configuration

Scenarios define specific test patterns with their own concurrency and ramp-up settings.

```yaml
"scenario_name":
  requests:
    - "request1"
    - "request2"
  min_concurrency: 1
  max_concurrency: 10
  ramp_up_multiply: [1, 2, 4, 8]
  ramp_up_wait: [5, 5, 5, 5]
  iterate_through_requests: true
  run_once: false
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requests` | list[string] | Yes | List of request names (must match request config) |
| `min_concurrency` | integer | Yes | Starting number of concurrent requests |
| `max_concurrency` | integer | Yes | Maximum number of concurrent requests |
| `ramp_up_multiply` | integer or list[integer] | No* | Multipliers for gradual request increase |
| `ramp_up_add` | integer or list[integer] | No* | Additive values for gradual request increase |
| `ramp_up_wait` | integer or list[integer] | No | Wait time between ramp-up steps in seconds (default: [0.1]) |
| `iterate_through_requests` | boolean | No | Whether to cycle through requests sequentially (default: false) |
| `run_once` | boolean | No | Whether to run the scenario only once (default: false) |

*Note: Either `ramp_up_multiply` or `ramp_up_add` must be specified, but not both.

## Request Configuration File

The request configuration file defines individual HTTP requests that can be referenced by scenarios.

### Structure

```yaml
requests:
  "request_name":
    url: "http://example.com/api/endpoint"
    method: "GET"
    expected_response_time: 1.0
    auth: null
    params:
      key: "value"
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Full URL for the request |
| `method` | string | Yes | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `expected_response_time` | number | Yes | Expected response time in seconds |
| `auth` | object/null | No | Authentication configuration (null for none) |
| `params` | object | No | Request parameters (for GET) or body data (for POST/PUT) |

## Ramp-up Strategies

Gradual supports two types of ramp-up strategies to gradually increase load on your system.

### Multiplicative Ramp-up

Use `ramp_up_multiply` to multiply the current request count by specified factors:

```yaml
ramp_up_multiply: [1, 2, 4, 8, 16]
ramp_up_wait: [5, 5, 5, 5, 5]
```

**Execution Flow:**
1. Start with 1 concurrent request
2. Wait 5 seconds, then multiply by 2 = 2 concurrent requests
3. Wait 5 seconds, then multiply by 4 = 8 concurrent requests
4. Wait 5 seconds, then multiply by 8 = 64 concurrent requests
5. Wait 5 seconds, then multiply by 16 = 1024 concurrent requests

### Additive Ramp-up

Use `ramp_up_add` to add specified numbers of requests:

```yaml
ramp_up_add: [1, 2, 3, 4, 5]
ramp_up_wait: [2, 2, 2, 2, 2]
```

**Execution Flow:**
1. Start with 1 concurrent request
2. Wait 2 seconds, then add 1 = 2 concurrent requests
3. Wait 2 seconds, then add 2 = 4 concurrent requests
4. Wait 2 seconds, then add 3 = 7 concurrent requests
5. Wait 2 seconds, then add 4 = 11 concurrent requests
6. Wait 2 seconds, then add 5 = 16 concurrent requests

### Ramp-up Wait Times

The `ramp_up_wait` field can be:
- **Single value**: Applied to all ramp-up steps
- **List of values**: Applied to each ramp-up step individually

```yaml
# Single value - wait 5 seconds between all steps
ramp_up_wait: 5

# List of values - wait different times between steps
ramp_up_wait: [5, 10, 15, 20]
```

## Configuration Examples

### Simple Load Test

```yaml
# test_config.yaml
runs:
  name: "Simple API Test"
  wait_between_phases: 0
  phases:
    "main_test":
      scenarios:
        "api_scenario":
          requests:
            - "health_check"
            - "get_data"
          min_concurrency: 1
          max_concurrency: 50
          ramp_up_multiply: [1, 2, 5, 10, 25, 50]
          ramp_up_wait: [10, 10, 10, 10, 10, 10]
          iterate_through_requests: true
      run_time: 300
```

```yaml
# request_config.yaml
requests:
  "health_check":
    url: "http://localhost:8000/health"
    method: "GET"
    expected_response_time: 0.5
    auth: null
  "get_data":
    url: "http://localhost:8000/api/data"
    method: "GET"
    expected_response_time: 1.0
    auth: null
```

### Multi-Phase Stress Test

```yaml
# test_config.yaml
runs:
  name: "Stress Test with Recovery"
  wait_between_phases: 30
  phases:
    "warm_up":
      scenarios:
        "light_load":
          requests:
            - "health_check"
          min_concurrency: 1
          max_concurrency: 10
          ramp_up_multiply: [1, 2, 5, 10]
          ramp_up_wait: [5, 5, 5, 5]
          iterate_through_requests: true
      run_time: 120
    "peak_load":
      scenarios:
        "heavy_load":
          requests:
            - "complex_operation"
            - "data_processing"
          min_concurrency: 10
          max_concurrency: 200
          ramp_up_multiply: [10, 25, 50, 100, 200]
          ramp_up_wait: [15, 15, 15, 15, 15]
          iterate_through_requests: true
      run_time: 600
    "recovery":
      scenarios:
        "recovery_test":
          requests:
            - "health_check"
          min_concurrency: 200
          max_concurrency: 1
          ramp_up_add: [-50, -50, -50, -49]
          ramp_up_wait: [10, 10, 10, 10]
          iterate_through_requests: true
      run_time: 180
```

```yaml
# request_config.yaml
requests:
  "health_check":
    url: "http://localhost:8000/health"
    method: "GET"
    expected_response_time: 0.5
    auth: null
  "complex_operation":
    url: "http://localhost:8000/api/complex"
    method: "POST"
    expected_response_time: 5.0
    auth: null
    params:
      operation: "heavy_computation"
      data_size: 1000
  "data_processing":
    url: "http://localhost:8000/api/process"
    method: "POST"
    expected_response_time: 3.0
    auth: null
    params:
      batch_size: 100
      priority: "high"
```

### Authentication Example

```yaml
# request_config.yaml
requests:
  "authenticated_endpoint":
    url: "http://localhost:8000/api/protected"
    method: "GET"
    expected_response_time: 1.0
    auth:
      type: "bearer"
      token: "your_auth_token"
    params: {}
```

## Advanced Configuration

### Dynamic Request Loading

For advanced use cases, you can reference requests from external files:

```yaml
# In test_config.yaml
scenarios:
  "dynamic_scenario":
    requests: "FROM_REQUEST_YAML_FILE"
    request_file: path/to/external_requests.yaml
    # ... other scenario configuration
```

### Single vs. List Values

Many configuration fields accept both single values and lists. When a single value is provided, it's automatically converted to a list:

```yaml
# These are equivalent:
ramp_up_multiply: 5
ramp_up_multiply: [5]

# These are equivalent:
ramp_up_wait: 10
ramp_up_wait: [10]
```

## Validation Rules

### Required Fields

- **Test Config**: `runs.name`, `runs.phases`, `phases.scenarios`, `scenarios.requests`, `scenarios.min_concurrency`, `scenarios.max_concurrency`, `phases.run_time`
- **Request Config**: `requests.url`, `requests.method`, `requests.expected_response_time`

### Value Constraints

- **Concurrency**: Must be positive integers
- **Timing**: Must be positive numbers
- **Ramp-up**: Must specify either `ramp_up_multiply` or `ramp_up_add`, but not both
- **Request References**: Request names in scenarios must exist in the request configuration

### Best Practices

1. **Naming**: Use descriptive names for phases, scenarios, and requests
2. **Structure**: Keep test structure and request definitions separate
3. **Reusability**: Define requests once and reuse across multiple scenarios
4. **Ramp-up**: Start with conservative ramp-up values and adjust based on system performance
5. **Phases**: Use phases to test different load patterns and allow system recovery
6. **Documentation**: Add comments to complex configurations for clarity

### Configuration-First Approach

Since the CLI doesn't support command-line overrides, adopt a configuration-first approach:

- **Version Control**: Keep all test configurations in version control for reproducibility
- **Environment-Specific Configs**: Create separate configuration files for different environments (dev, staging, prod)
- **Configuration Templates**: Use base templates and extend them for specific test scenarios
- **Parameterization**: Use YAML anchors and aliases to avoid duplication
- **Validation**: Always validate your YAML syntax before running tests

Example of using YAML anchors for reusability:

```yaml
# test_config.yaml
runs:
  name: "Parameterized Test"
  wait_between_phases: 10
  phases:
    "light_load": &light_load
      scenarios:
        "light_scenario":
          requests: ["health_check", "simple_api"]
          min_concurrency: 1
          max_concurrency: 10
          ramp_up_multiply: [1, 2, 5, 10]
          ramp_up_wait: [5, 5, 5, 5]
          iterate_through_requests: true
      run_time: 120
    
    "medium_load":
      <<: *light_load  # Inherit from light_load
      scenarios:
        "medium_scenario":
          <<: *light_load.scenarios.light_scenario  # Inherit scenario config
          max_concurrency: 50
          ramp_up_multiply: [1, 5, 15, 30, 50]
          ramp_up_wait: [10, 10, 10, 10, 10]
      run_time: 300
```

## Troubleshooting Configuration Issues

### Common Errors

1. **Missing Request Definition**: Ensure all request names in scenarios exist in the request configuration
2. **Invalid Ramp-up**: Check that either `ramp_up_multiply` or `ramp_up_add` is specified, but not both
3. **Type Mismatches**: Verify that numeric fields contain valid numbers
4. **File Paths**: Ensure configuration files are in the correct locations

### Debug Tips

- Use the `--debug` flag when running tests to see detailed configuration parsing
- Check YAML syntax with a YAML validator
- Verify file permissions and paths
- Test with minimal configurations first, then add complexity gradually
