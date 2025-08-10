# User Guide

Learn how to use Gradual for stress testing your applications and systems.

## Getting Started

If you're new to Gradual, start with these guides:

- **[Installation Guide](installation.md)** - Complete setup and installation instructions
- **[Getting Started Guide](getting_started.md)** - Run your first test and learn the basics

## Quick Reference

For experienced users, here's a quick reference of the main commands:

```bash
# Run a stress test
stress-run --test_config test_config.yaml

# Run with request configuration
stress-run --test_config test_config.yaml --request_config request_config.yaml

# Start the monitoring dashboard
stress-dashboard --mode bokeh --port 8080
```

## Configuration

Gradual uses a two-file configuration system that provides flexibility and clarity:

1. **Test Configuration** (`test_config.yaml`) - Defines test structure, phases, and scenarios
2. **Request Configuration** (`request_config.yaml`) - Defines individual HTTP requests

> **📖 💡 Need detailed configuration options? Check out the dedicated [Configuration Reference](configuration_reference.md) tab in the navigation for a complete guide to all available settings, examples, and best practices.**

This section provides a quick overview of the configuration structure. For comprehensive configuration details, advanced examples, and troubleshooting tips, use the **Configuration** tab in the left navigation.

### Test Configuration Structure

The main test configuration file defines the overall test structure:

```yaml
runs:
  name: "Test Run Name"                    # Name of the test run
  wait_between_phases: 10                  # Wait time between phases (seconds)
  phases:                                  # Test phases
    "phase1":                              # Phase name
      scenarios:                           # Scenarios within this phase
        "scenario1":                       # Scenario name
          requests:                        # List of request names
            - "request1"
            - "request2"
          min_concurrency: 1               # Minimum concurrent requests
          max_concurrency: 10              # Maximum concurrent requests
          ramp_up_multiply:                # Ramp-up multipliers (can be list or single value)
            - 1
            - 2
            - 3
          ramp_up_wait:                    # Wait time between ramp-up steps (seconds)
            - 1
            - 2
            - 3
          iterate_through_requests: true   # Whether to iterate through requests
        "scenario2":                       # Another scenario
          requests:
            - "request3"
          min_concurrency: 1
          max_concurrency: 10
          ramp_up_multiply: 1              # Single value (will be converted to list)
          ramp_up_wait: 1                  # Single value (will be converted to list)
          iterate_through_requests: true
      run_time: 10                         # Phase duration (seconds)
```

### Request Configuration Structure

The request configuration file defines individual HTTP requests:

```yaml
requests:
  "request1":                              # Request name (referenced in test config)
    url: "http://localhost:8000/ping"      # Full URL
    method: "GET"                          # HTTP method
    expected_response_time: 1               # Expected response time (seconds)
    auth: null                             # Authentication (null for none)
  "request2":
    url: "http://localhost:8000/data"
    method: "GET"
    expected_response_time: 1
    auth: null
  "request3":
    url: "http://localhost:8000/submit"
    method: "POST"
    expected_response_time: 1
    auth: null
    params:                                # Request parameters/body
      name: "John Doe"
      email: "john.doe@example.com"
      age: 30
      city: "New York"
      country: "USA"
```

## Configuration Options

### Phase Configuration

- **`name`**: Unique identifier for the phase
- **`scenarios`**: Dictionary of scenarios to run in this phase
- **`run_time`**: Duration of the phase in seconds

### Scenario Configuration

- **`requests`**: List of request names (must match names in request config)
- **`min_concurrency`**: Starting number of concurrent requests
- **`max_concurrency`**: Maximum number of concurrent requests
- **`ramp_up_multiply`**: Multipliers for gradual request increase (list or single value)
- **`ramp_up_wait`**: Wait time between ramp-up steps in seconds (list or single value)
- **`iterate_through_requests`**: Whether to cycle through requests sequentially
- **`run_once`**: Whether to run the scenario only once (optional)

### Request Configuration

- **`url`**: Full URL for the request
- **`method`**: HTTP method (GET, POST, PUT, DELETE, etc.)
- **`expected_response_time`**: Expected response time in seconds
- **`auth`**: Authentication configuration (null for none)
- **`params`**: Request parameters (for GET) or body data (for POST/PUT)

## Ramp-up Configuration

Gradual supports two types of ramp-up strategies:

### Multiplicative Ramp-up

```yaml
ramp_up_multiply: [1, 2, 4, 8, 16]    # Multiply requests by these factors
ramp_up_wait: [5, 5, 5, 5, 5]          # Wait 5 seconds between each step
```

This will:
1. Start with 1 concurrent request
2. Wait 5 seconds, then increase to 2 concurrent requests
3. Wait 5 seconds, then increase to 4 concurrent requests
4. Wait 5 seconds, then increase to 8 concurrent requests
5. Wait 5 seconds, then increase to 16 concurrent requests

### Additive Ramp-up

```yaml
ramp_up_add: [1, 2, 3, 4, 5]           # Add these numbers of requests
ramp_up_wait: [2, 2, 2, 2, 2]          # Wait 2 seconds between each step
```

This will:
1. Start with 1 concurrent request
2. Wait 2 seconds, then add 1 request (total: 2)
3. Wait 2 seconds, then add 2 requests (total: 4)
4. Wait 2 seconds, then add 3 requests (total: 7)
5. Wait 2 seconds, then add 4 requests (total: 11)
6. Wait 2 seconds, then add 5 requests (total: 16)

## Advanced Features

### Request Iteration

When `iterate_through_requests: true`, Gradual will cycle through the requests in the scenario sequentially. This is useful for simulating realistic request workflows.

### Phase Sequencing

Phases run sequentially with the specified `wait_between_phases` delay. This allows you to:
- Test different load patterns
- Implement complex test scenarios
- Allow system recovery between phases

### Dynamic Request Loading

For advanced use cases, you can reference requests from external files:

```yaml
requests: "FROM_REQUEST_YAML_FILE"
request_file: path/to/requests.yaml
```

## Best Practices

### 1. Test Design

- **Start Small**: Begin with low concurrency and gradually increase
- **Realistic Scenarios**: Model realistic request patterns
- **Phase Planning**: Use phases to test different load patterns
- **Request Sequencing**: Use `iterate_through_requests` for realistic workflows

### 2. Ramp-up Strategy

- **Gradual Increase**: Use ramp-up to avoid overwhelming the system
- **Monitor Performance**: Watch for performance degradation during ramp-up
- **Realistic Timing**: Set appropriate wait times between ramp-up steps

---

> **📖 💡 Ready to dive deeper into configuration? The [Configuration Reference](configuration_reference.md) tab contains comprehensive examples, advanced options, validation rules, troubleshooting tips, and best practices for complex scenarios.**

### 3. Configuration Management

- **Separate Concerns**: Keep test structure and request definitions separate
- **Reusable Requests**: Define requests once and reuse across scenarios
- **Clear Naming**: Use descriptive names for phases, scenarios, and requests

## Example Configurations

### Basic Load Test

```yaml
# test_config.yaml
runs:
  name: "Basic Load Test"
  wait_between_phases: 5
  phases:
    "ramp_up":
      scenarios:
        "basic_scenario":
          requests:
            - "health_check"
            - "api_endpoint"
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
  "api_endpoint":
    url: "http://localhost:8000/api/data"
    method: "GET"
    expected_response_time: 1.0
    auth: null
```

### Multi-Phase Test

```yaml
# test_config.yaml
runs:
  name: "Multi-Phase Test"
  wait_between_phases: 10
  phases:
    "warm_up":
      scenarios:
        "warm_up_scenario":
          requests:
            - "light_request"
          min_concurrency: 1
          max_concurrency: 10
          ramp_up_multiply: [1, 2, 5, 10]
          ramp_up_wait: [5, 5, 5, 5]
          iterate_through_requests: true
      run_time: 120
    "peak_load":
      scenarios:
        "peak_scenario":
          requests:
            - "heavy_request"
            - "data_processing"
          min_concurrency: 10
          max_concurrency: 100
          ramp_up_multiply: [10, 25, 50, 75, 100]
          ramp_up_wait: [10, 10, 10, 10, 10]
          iterate_through_requests: true
      run_time: 300
    "cool_down":
      scenarios:
        "cool_down_scenario":
          requests:
            - "light_request"
          min_concurrency: 100
          max_concurrency: 1
          ramp_up_add: [-20, -20, -20, -20, -19]
          ramp_up_wait: [5, 5, 5, 5, 5]
          iterate_through_requests: true
      run_time: 120
```

## Troubleshooting

### Common Issues

#### Configuration Errors

- **Missing Fields**: Ensure all required fields are present
- **Invalid Values**: Check that numeric values are positive
- **Request References**: Verify request names match between config files

#### Performance Issues

- **Ramp-up Too Fast**: Increase wait times between ramp-up steps
- **High Error Rates**: Reduce concurrency or check target system health
- **Memory Issues**: Monitor system resources during tests

### Running Tests

```bash
# Run with configuration files
stress-run --test_config my_test.yaml --request_config requests.yaml

# Run with only test configuration (requests defined inline)
stress-run --test_config my_test.yaml
```

> **⚠️ Note:** All test parameters must be defined in the YAML configuration files. The CLI does not support command-line overrides.

## Next Steps

- **New to Gradual?** Start with the [Installation Guide](installation.md) and [Getting Started Guide](getting_started.md)
- **Ready for more?** Explore the [API Reference](api/) for detailed technical information
- **Looking for examples?** Check out [Examples](examples.md) for real-world use cases
- **Want to contribute?** Learn about [Development](dev_guide.md)
- **Need help?** Join the [community discussions](https://github.com/Gradual-Load-Testing/gradual/discussions)
