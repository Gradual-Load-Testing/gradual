# Examples

This page provides real-world examples of using the Gradual stress testing framework.

## Sample Configuration Examples

These examples are based on the actual configuration files included with Gradual.

### Basic FastAPI Test Configuration

This example shows a simple test configuration for a FastAPI application with two scenarios.

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
          ramp_up_multiply:
            - 1
            - 2
            - 3
          ramp_up_wait:
            - 1
            - 2
            - 3
          iterate_through_requests: true
        "scenario2":
          requests:
            - "request3"
          min_concurrency: 1
          max_concurrency: 10
          ramp_up_multiply: 1
          ramp_up_wait: 1
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
  "request3":
    url: "http://localhost:8000/submit"
    method: "POST"
    expected_response_time: 1
    auth: null
    params:
      name: "John Doe"
      email: "john.doe@example.com"
      age: 30
      city: "New York"
      country: "USA"
```

**What This Test Does:**
1. **Phase 1** runs for 10 seconds with two scenarios:
   - **Scenario 1**: Tests two GET endpoints (`/ping` and `/data`) with ramp-up from 1 to 10 concurrent requests
- **Scenario 2**: Tests a POST endpoint (`/submit`) with a single concurrent request
2. **Ramp-up Strategy**: Concurrent requests multiply by 1, 2, then 3, with waits of 1, 2, then 3 seconds
3. **Request Iteration**: Both scenarios iterate through their requests sequentially

### Running the Example

```bash
# Navigate to the example directory
cd examples/fastapi_app

# Run the stress test
stress-run stress_test_configs/test_config.yaml

# Or specify both config files explicitly
stress-run stress_test_configs/test_config.yaml --request-config stress_test_configs/request_config.yaml
```

## Basic Examples

### Simple HTTP API Test

```yaml
# simple_api_test.yaml
runs:
  name: "Simple API Test"
  wait_between_phases: 0
  phases:
    "api_test":
      run_time: 120
      scenarios:
        "get_posts":
          requests:
            - "get_post"
          min_concurrency: 1
          max_concurrency: 50
          ramp_up_add: 10
          ramp_up_wait: 30
          iterate_through_requests: false
```

**Request Configuration** (`requests.yaml`):
```yaml
requests:
  "get_post":
    url: "https://jsonplaceholder.typicode.com/posts/1"
    method: "GET"
    expected_response_time: 1000
    auth: null
    params: {}
```

### Multi-Scenario Test

```yaml
# multi_scenario_test.yaml
runs:
  name: "E-commerce API Test"
  wait_between_phases: 5
  phases:
    "browse_phase":
      run_time: 300
      scenarios:
        "browse_products":
          requests:
            - "get_products"
          min_concurrency: 10
          max_concurrency: 100
          ramp_up_add: 20
          ramp_up_wait: 60
          iterate_through_requests: false
    
    "cart_phase":
      run_time: 300
      scenarios:
        "add_to_cart":
          requests:
            - "add_cart_item"
          min_concurrency: 5
          max_concurrency: 50
          ramp_up_add: 10
          ramp_up_wait: 60
          iterate_through_requests: false
```

**Request Configuration** (`ecommerce_requests.yaml`):
```yaml
requests:
  "get_products":
    url: "https://api.ecommerce.com/products"
    method: "GET"
    expected_response_time: 2000
    auth: null
    params:
      category: "electronics"
      page: "1"
  
  "add_cart_item":
    url: "https://api.ecommerce.com/cart/add"
    method: "POST"
    expected_response_time: 3000
    auth: "Bearer {{auth_token}}"
    params:
      product_id: "prod_001"
      quantity: 1
```

## Advanced Examples

### Authentication Testing

```yaml
# auth_test.yaml
runs:
  name: "Authentication Test"
  wait_between_phases: 10
  phases:
    "login_test":
      run_time: 180
      scenarios:
        "valid_login":
          requests:
            - "login_valid"
          min_concurrency: 5
          max_concurrency: 50
          ramp_up_add: 10
          ramp_up_wait: 30
          iterate_through_requests: false
        
        "invalid_login":
          requests:
            - "login_invalid"
          min_concurrency: 2
          max_concurrency: 20
          ramp_up_add: 5
          ramp_up_wait: 30
          iterate_through_requests: false
    
    "protected_endpoints":
      run_time: 180
      scenarios:
        "user_profile":
          requests:
            - "get_profile"
          min_concurrency: 10
          max_concurrency: 100
          ramp_up_add: 20
          ramp_up_wait: 30
          iterate_through_requests: false
```

**Request Configuration** (`auth_requests.yaml`):
```yaml
requests:
  "login_valid":
    url: "https://api.example.com/auth/login"
    method: "POST"
    expected_response_time: 2000
    auth: null
    params:
      username: "user1"
      password: "pass1"
  
  "login_invalid":
    url: "https://api.example.com/auth/login"
    method: "POST"
    expected_response_time: 2000
    auth: null
    params:
      username: "invalid"
      password: "wrong"
  
  "get_profile":
    url: "https://api.example.com/users/profile"
    method: "GET"
    expected_response_time: 1500
    auth: "Bearer {{auth_token}}"
    params: {}
```

### Database Testing

```yaml
# database_test.yaml
runs:
  name: "Database Performance Test"
  wait_between_phases: 15
  phases:
    "read_operations":
      run_time: 300
      scenarios:
        "user_reads":
          requests:
            - "get_user"
          min_concurrency: 20
          max_concurrency: 200
          ramp_up_add: 40
          ramp_up_wait: 60
          iterate_through_requests: false
    
    "write_operations":
      run_time: 300
      scenarios:
        "user_creation":
          requests:
            - "create_user"
          min_concurrency: 5
          max_concurrency: 50
          ramp_up_add: 10
          ramp_up_wait: 60
          iterate_through_requests: false
```

**Request Configuration** (`db_requests.yaml`):
```yaml
requests:
  "get_user":
    url: "https://api.example.com/users/{{user_id}}"
    method: "GET"
    expected_response_time: 500
    auth: "Bearer {{auth_token}}"
    params: {}
  
  "create_user":
    url: "https://api.example.com/users"
    method: "POST"
    expected_response_time: 1000
    auth: "Bearer {{admin_token}}"
    params:
      username: "newuser1"
      email: "new1@example.com"
      role: "user"
```

## Performance Testing Examples

### Load Testing with Ramp-up

```yaml
# ramp_up_test.yaml
runs:
  name: "Ramp-up Load Test"
  wait_between_phases: 0
  phases:
    "health_check":
      run_time: 1800  # 30 minutes
      scenarios:
        "api_health":
          requests:
            - "health_endpoint"
          min_concurrency: 10
          max_concurrency: 1000
          ramp_up_add: 100
          ramp_up_wait: 900  # 15 minutes ramp-up
          iterate_through_requests: false
```

**Request Configuration** (`health_requests.yaml`):
```yaml
requests:
  "health_endpoint":
    url: "https://api.example.com/health"
    method: "GET"
    expected_response_time: 100
    auth: null
    params: {}
```

### Stress Testing

```yaml
# stress_test.yaml
runs:
  name: "Stress Test"
  wait_between_phases: 0
  phases:
    "heavy_operations":
      run_time: 600  # 10 minutes
      scenarios:
        "complex_processing":
          requests:
            - "process_data"
          min_concurrency: 50
          max_concurrency: 500
          ramp_up_add: 100
          ramp_up_wait: 60
          iterate_through_requests: false
```

**Request Configuration** (`stress_requests.yaml`):
```yaml
requests:
  "process_data":
    url: "https://api.example.com/process"
    method: "POST"
    expected_response_time: 10000  # 10 seconds
    auth: "Bearer {{auth_token}}"
    params:
      data: "large_dataset"
      operation: "complex_calculation"
```

## Custom Extensions Examples

### Custom Configuration Parser

```python
# custom_parser.py
from gradual.configs.parser import Parser
import yaml

class ExtendedParser(Parser):
    """Extended parser with additional configuration options."""
    
    def __init__(self, test_config_file_path: str, request_configs_path: str):
        super().__init__(test_config_file_path, request_configs_path)
        self.custom_options = {}
    
    def read_configs(self):
        """Read and parse configuration files with custom extensions."""
        super().read_configs()
        
        # Read custom configuration options
        with open(self.test_config_file_path, "r") as config_file:
            config_data = yaml.safe_load(config_file)
            self.custom_options = config_data.get("custom_options", {})
    
    def get_custom_option(self, key: str, default=None):
        """Get custom configuration option."""
        return self.custom_options.get(key, default)
```

### Custom Runner

```python
# custom_runner.py
from gradual.runners.runner import Runner
import logging

class LoggingRunner(Runner):
    """Custom runner with enhanced logging."""
    
    def __init__(self, scenarios):
        super().__init__(scenarios)
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
    
    def start_test(self):
        """Start test execution with enhanced logging."""
        self.logger.info(f"Starting test with {len(self.scenarios)} scenarios")
        self.logger.info(f"Total expected requests: {self._calculate_total_requests()}")
        
        super().start_test()
        
        self.logger.info(f"Test completed. Total requests processed: {self.request_count}")
    
    def _calculate_total_requests(self):
        """Calculate total expected requests across all scenarios."""
        total = 0
        for scenario in self.scenarios:
            # This is a simplified calculation - actual implementation would be more complex
            total += scenario.max_concurrency * scenario.runtime
        return total
```

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/stress-test.yml
name: "Stress Testing"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  stress-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    
    - name: Run stress tests
      run: |
        stress-run --test_config tests/stress/api_test.yaml --request_config tests/stress/requests.yaml
    
    - name: Generate report
      run: |
        stress-run --test_config tests/stress/api_test.yaml --request_config tests/stress/requests.yaml
    
    - name: Upload report
      uses: actions/upload-artifact@v3
      with:
        name: stress-test-report
        path: ./reports
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Gradual
RUN pip install -e ".[dev]"

# Expose ports
EXPOSE 8080

# Default command
CMD ["python", "-m", "gradual.main"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  gradual:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./tests:/app/tests
      - ./results:/app/results
    environment:
      - GRADUAL_LOG_LEVEL=INFO
    command: ["python", "-m", "gradual.main"]
```

## Monitoring and Reporting

### Custom Metrics Collection

```python
# custom_metrics.py
import time
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TestMetrics:
    """Custom metrics collection for test runs."""
    start_time: float
    end_time: float = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0
    
    def record_request(self, success: bool, response_time: float):
        """Record a single request result."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.total_response_time += response_time
    
    def finalize(self):
        """Finalize metrics collection."""
        self.end_time = time.time()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        duration = self.end_time - self.start_time
        avg_response_time = self.total_response_time / self.total_requests if self.total_requests > 0 else 0
        
        return {
            "duration_seconds": duration,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "average_response_time": avg_response_time,
            "requests_per_second": self.total_requests / duration if duration > 0 else 0
        }
```

### Simple Dashboard

```python
# simple_dashboard.py
import time
from typing import Dict, Any
from custom_metrics import TestMetrics

class SimpleDashboard:
    """Simple real-time dashboard for monitoring test progress."""
    
    def __init__(self):
        self.metrics = TestMetrics(start_time=time.time())
        self.running = True
    
    def update_metrics(self, success: bool, response_time: float):
        """Update metrics with new request data."""
        self.metrics.record_request(success, response_time)
    
    def display_status(self):
        """Display current test status."""
        if not self.running:
            return
        
        summary = self.metrics.get_summary()
        print(f"\n=== Test Status ===")
        print(f"Duration: {summary['duration_seconds']:.1f}s")
        print(f"Total Requests: {summary['total_requests']}")
        print(f"Success Rate: {summary['success_rate']:.2%}")
        print(f"Avg Response Time: {summary['average_response_time']:.3f}s")
        print(f"Requests/sec: {summary['requests_per_second']:.1f}")
        print("=" * 20)
    
    def stop(self):
        """Stop the dashboard."""
        self.running = False
        self.metrics.finalize()
        print("\n=== Final Results ===")
        final_summary = self.metrics.get_summary()
        for key, value in final_summary.items():
            if isinstance(value, float):
                print(f"{key}: {value:.3f}")
            else:
                print(f"{key}: {value}")
```

## Best Practices

### Test Design

1. **Realistic Scenarios**: Model real user behavior
2. **Data Variation**: Use different data sets
3. **Ramp-up Strategy**: Start with low concurrency and gradually increase
4. **Error Handling**: Test both success and failure scenarios

### Environment Setup

1. **Isolation**: Use dedicated test environments
2. **Monitoring**: Set up comprehensive monitoring
3. **Cleanup**: Implement data cleanup procedures
4. **Backup**: Have rollback plans

### Analysis

1. **Baselines**: Establish performance baselines
2. **Trends**: Monitor performance over time
3. **Bottlenecks**: Identify and document bottlenecks
4. **Documentation**: Document findings and recommendations

## Next Steps

- Explore the [API Reference](/gradual/api/overview/) for detailed technical information
- Read the [User Guide](user_guide.md) for comprehensive usage instructions
- Check the [Development Guide](dev_guide.md) for contribution guidelines
- Join the [community discussions](https://github.com/Gradual-Load-Testing/gradual/discussions)
