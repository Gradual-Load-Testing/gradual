# Getting Started Guide

Welcome to Gradual! This guide will help you run your first stress test and understand the basic concepts. By the end of this guide, you'll have successfully executed a load test and viewed the results.

## Prerequisites

Before you begin, ensure you have:

- ✅ **Gradual installed** - Follow the [Installation Guide](installation.md) if you haven't installed it yet
- ✅ **A target application** - A web service, API, or application to test
- ✅ **Basic understanding** - Familiarity with HTTP requests and YAML configuration

## Quick Start: Your First Test

### Step 1: Create a Simple Test Configuration

Create a file named `first_test.yaml` with the following content:

```yaml
name: "My First Stress Test"
description: "A simple test to get started with Gradual"

target:
  base_url: "https://httpbin.org"
  protocol: "http"

scenarios:
  - name: "Get Request"
    weight: 100
    steps:
      - request:
          method: "GET"
          path: "/get"
        assertions:
          - status_code: 200
          - response_time: "< 2000ms"

load:
  users: 10
  duration: 60
  ramp_up: 10
```

**Note**: We're using `httpbin.org` as a test target since it's a public service designed for testing HTTP requests.

### Step 2: Run Your First Test

Open a terminal and run:

```bash
stress-run first_test.yaml
```

You should see output similar to:

```
🚀 Starting stress test: My First Stress Test
📊 Target: https://httpbin.org
👥 Users: 10 | Duration: 60s | Ramp-up: 10s
⏱️  Test started at 2024-01-15 10:30:00

[████████████████████████████████████████] 100% | 60s elapsed
✅ Test completed successfully!

📈 Results Summary:
   Total Requests: 1,200
   Successful: 1,200 (100.0%)
   Failed: 0 (0.0%)
   Average Response Time: 245ms
   95th Percentile: 456ms
   Requests/Second: 20.0
```

### Step 3: View Real-time Results

In another terminal, start the dashboard to monitor your test in real-time:

```bash
stress-dashboard --mode bokeh --port 8080
```

Open your browser and navigate to `http://localhost:8080` to see live metrics.

## Understanding the Test Configuration

Let's break down the key components of your test configuration:

### Test Metadata
```yaml
name: "My First Stress Test"        # Name of your test
description: "A simple test..."     # Description for documentation
```

### Target Configuration
```yaml
target:
  base_url: "https://httpbin.org"   # The system you're testing
  protocol: "http"                  # Protocol to use
```

### Test Scenarios
```yaml
scenarios:
  - name: "Get Request"             # Name of this test scenario
    weight: 100                     # Relative frequency (100 = 100%)
    steps:                          # List of actions to perform
      - request:                    # HTTP request configuration
          method: "GET"             # HTTP method
          path: "/get"              # Path relative to base_url
```

### Load Configuration
```yaml
load:
  users: 10                        # Number of concurrent users
  duration: 60                     # Test duration in seconds
  ramp_up: 10                      # Time to gradually increase users
```

## Creating Your Own Test

Now let's create a test for your own application. Here's a template:

```yaml
name: "My Application Test"
description: "Testing my web application"

target:
  base_url: "http://localhost:3000"  # Change this to your app's URL
  protocol: "http"

scenarios:
  - name: "Homepage Load"
    weight: 50
    steps:
      - request:
          method: "GET"
          path: "/"
        assertions:
          - status_code: 200
          - response_time: "< 1000ms"

  - name: "API Endpoint"
    weight: 50
    steps:
      - request:
          method: "POST"
          path: "/api/data"
          headers:
            Content-Type: "application/json"
          body:
            key: "value"
        assertions:
          - status_code: 200
          - response_time: "< 500ms"

load:
  users: 20
  duration: 120
  ramp_up: 30
```

### Running Tests

Run your stress tests using the CLI:

```bash
# Run with both configuration files
stress-run --test_config my_test.yaml --request_config requests.yaml

# Run with only test configuration (requests defined inline)
stress-run --test_config my_test.yaml

# Run with relative paths
stress-run --test_config ./configs/test.yaml --request_config ./configs/requests.yaml
```

> **⚠️ Note:** All test parameters must be defined in the YAML configuration files. The CLI does not support command-line overrides.

## Monitoring Your Tests

### Real-time Dashboard

The dashboard provides live monitoring:

```bash
# Start Bokeh dashboard (interactive charts)
stress-dashboard --mode bokeh --port 8080

# Start WebSocket dashboard (lightweight)
stress-dashboard --mode websocket --port 8081

# Start with custom host
stress-dashboard --mode bokeh --host 0.0.0.0 --port 8080
```

### Key Metrics to Watch

- **Response Time**: How fast your application responds
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests
- **Active Users**: Current load on your system

## Common Test Patterns

### 1. Smoke Test (Light Load)
```yaml
load:
  users: 5
  duration: 60
  ramp_up: 10
```

### 2. Load Test (Normal Load)
```yaml
load:
  users: 50
  duration: 300
  ramp_up: 60
```

### 3. Stress Test (High Load)
```yaml
load:
  users: 200
  duration: 600
  ramp_up: 120
```

### 4. Spike Test (Sudden Load)
```yaml
load:
  users: 100
  duration: 180
  ramp_up: 10  # Quick ramp-up for spike effect
```

## Best Practices for Beginners

### 1. Start Small
- Begin with a small number of users (5-10)
- Use short durations (1-2 minutes)
- Gradually increase load

### 2. Test in Isolation
- Use dedicated test environments
- Avoid testing production systems initially
- Clean up test data after runs

### 3. Monitor Everything
- Watch your target application's performance
- Monitor system resources (CPU, memory, network)
- Use the dashboard for real-time insights

### 4. Validate Results
- Check that assertions are passing
- Verify response times are reasonable
- Ensure error rates are acceptable

## Troubleshooting Common Issues

### Test Won't Start
```bash
# Check if Gradual is installed
stress-run --version

# Verify your YAML syntax
python -c "import yaml; yaml.safe_load(open('test.yaml'))"
```

### High Error Rates
```bash
# Check if target is accessible
curl http://localhost:3000

# Run with debug mode
stress-run test.yaml --debug --verbose
```

### Dashboard Not Loading
```bash
# Check if port is available
netstat -tulpn | grep 8080

# Try different port
stress-dashboard --mode bokeh --port 8081
```

## Next Steps

Congratulations! You've successfully run your first stress test. Here's what to explore next:

1. **Read the [User Guide](user_guide.md)** for advanced features and detailed configuration
2. **Check out [Examples](examples.md)** for real-world test scenarios
3. **Learn about [Custom Protocol Handlers](user_guide.md#custom-protocol-handlers)** for specialized testing
4. **Explore [Distributed Testing](user_guide.md#distributed-testing)** for large-scale tests
5. **Dive into the [Configuration Reference](configuration_reference.md)** for comprehensive configuration options and examples

> **💡 Tip:** Use the **Configuration** tab in the navigation for quick access to all configuration options and best practices.

## Getting Help

- **Documentation**: Browse the complete documentation
- **Examples**: Study the example configurations
- **Community**: Join discussions on GitHub
- **Issues**: Report bugs or request features

Happy testing! 🚀
