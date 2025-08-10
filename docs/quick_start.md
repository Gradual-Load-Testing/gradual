# Quick Start Guide

Get up and running with Gradual stress testing in minutes using the included sample configurations.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Basic knowledge of YAML configuration files

## Installation

```bash
# Clone the repository
git clone https://github.com/Gradual-Load-Testing/gradual.git
cd gradual

# Install Gradual with development dependencies
pip install -e ".[dev,bokeh,websockets]"
```

## Your First Stress Test

Gradual comes with sample configuration files that you can use immediately to test your understanding.

### 1. Explore the Sample Configuration

Navigate to the examples directory:

```bash
cd examples/fastapi_app/stress_test_configs
```

You'll find two files:

- `test_config.yaml` - Defines the test structure
- `request_config.yaml` - Defines the HTTP and WebSocket requests

### 2. Understand the Configuration

**Test Configuration** (`test_config.yaml`):
```yaml
runs:
  name: "Test Run"
  wait_between_phases: 10
  phases:
    "phase1":
      scenarios:
        "scenario1":
          requests:
            - "request1"
            - "request2"
          min_concurrency: 1
          max_concurrency: 10
          ramp_up_multiply: [1, 2, 3]
          ramp_up_wait: [1, 2, 3]
          iterate_through_requests: true
      run_time: 10
```

**Request Configuration** (`request_config.yaml`):
```yaml
requests:
  "request1":
    url: "http://localhost:8000/ping"
    method: "GET"
    expected_response_time: 1
    auth: null
  "request2":
    url: "http://localhost:8000/data"
    method: "GET"
    expected_response_time: 1
    auth: null
```

### 3. Run Your First Test

```bash
# From the examples/fastapi_app directory
stress-run --test_config stress_test_configs/test_config.yaml
```

**What Happens:**

1. Gradual reads the test configuration
2. Starts with 1 concurrent request
3. Ramp-up: 1 → 2 → 3 concurrent requests (waiting 1, 2, 3 seconds between steps)
4. Runs for 10 seconds
5. Tests two endpoints: `/ping` and `/data`

### 4. Monitor the Test

Open another terminal and start the monitoring dashboard:

```bash
stress-dashboard --mode bokeh --port 8080
```

Then open your browser to `http://localhost:8080` to see real-time metrics.

## Understanding the Results

After the test completes, you'll see:

- **Total Requests**: Number of requests made
- **Success Rate**: Percentage of successful requests
- **Response Times**: Average, 95th percentile, 99th percentile
- **Throughput**: Requests per second
- **Error Details**: Any failed requests and their reasons

## Customizing Your Test

### Modify the Sample Configuration

1. **Change the target URL** in `request_config.yaml`:
```yaml
requests:
  "request1":
    url: "https://your-api.com/health"  # Change this
    method: "GET"
    expected_response_time: 1
    auth: null
```

2. **Adjust the load** in `test_config.yaml`:
```yaml
scenarios:
  "scenario1":
    min_concurrency: 1
    max_concurrency: 50        # Increase this
    ramp_up_multiply: [1, 5, 10, 25, 50]  # More gradual ramp-up
    ramp_up_wait: [10, 10, 10, 10, 10]    # Longer waits
```

3. **Add more requests**:
```yaml
requests:
  "request1":
    url: "https://your-api.com/health"
    method: "GET"
    expected_response_time: 1
    auth: null
  "request2":
    url: "https://your-api.com/endpoints"
    method: "GET"
    expected_response_time: 2
    auth: null
  "request3":
    url: "https://your-api.com/submit"
    method: "POST"
    expected_response_time: 3
    auth: null
    params:
      name: "Test User"
      email: "test@example.com"
```

## Test Different Load Patterns

### Spike Test (sudden load increase):
```yaml
scenarios:
  "spike_test":
    min_concurrency: 1
    max_concurrency: 100
    ramp_up_multiply: [1, 100]  # Jump from 1 to 100 concurrent requests
    ramp_up_wait: [0, 0]        # No wait between steps
    iterate_through_requests: true
```

### Gradual Ramp-up (steady increase):
```yaml
scenarios:
  "gradual_test":
    min_concurrency: 1
    max_concurrency: 50
    ramp_up_multiply: [1, 2, 5, 10, 25, 50]
    ramp_up_wait: [30, 30, 30, 30, 30, 30]  # 30 seconds between steps
    iterate_through_requests: true
```

### Steady State (constant load):
```yaml
scenarios:
  "steady_test":
    min_concurrency: 50
    max_concurrency: 50
    ramp_up_multiply: [50]      # Start immediately with 50 concurrent requests
    ramp_up_wait: [0]           # No ramp-up wait
    iterate_through_requests: true
```

## Common Commands

```bash
# Run a test with configuration files
stress-run --test_config config.yaml --request_config requests.yaml

# Run with only test configuration (requests defined inline)
stress-run --test_config config.yaml

# Run with relative paths
stress-run --test_config ./configs/test.yaml --request_config ./configs/requests.yaml
```

## Next Steps

1. **Read the [User Guide](user_guide.md)** for comprehensive usage information
2. **Explore the [Configuration Reference](configuration_reference.md)** for all available options
3. **Check out [Examples](examples.md)** for more complex test scenarios
4. **Learn about [Development](dev_guide.md)** if you want to contribute

## Troubleshooting

### Common Issues

**"No module named 'gradual'"**
```bash
# Make sure you're in the project directory and have installed it
cd gradual
pip install -e ".[dev,bokeh,websockets]"
```

**"Configuration file not found"**
```bash
# Check your current directory and file paths
pwd
ls -la
```

**"Invalid configuration"**
```bash
# Validate your YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

**"Connection refused"**
- Ensure your target application is running
- Check the URL and port in your configuration
- Verify firewall settings

### Getting Help

- 📖 **Documentation**: Check the [User Guide](user_guide.md) and [Configuration Reference](configuration_reference.md)
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/Gradual-Load-Testing/gradual/issues)
- 💬 **Discussions**: Ask questions on [GitHub Discussions](https://github.com/Gradual-Load-Testing/gradual/discussions)

## Congratulations!

You've successfully run your first stress test with Gradual! You now understand:

- How to configure tests using YAML files
- How to run stress tests from the command line
- How to monitor tests in real-time
- How to customize test parameters

Continue exploring the documentation to learn about advanced features like:

- Multi-phase testing
- Authentication
- Custom protocol handlers
- Distributed testing
- Advanced reporting
