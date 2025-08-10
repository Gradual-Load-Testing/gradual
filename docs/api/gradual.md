# Gradual Package API Reference

This page provides the complete API reference for the Gradual stress testing framework.

## Package Overview

The `gradual` package is the main entry point for the stress testing framework. It provides high-level interfaces for configuring and running stress tests.

## Main Modules

### gradual.base

Base classes and interfaces for extending the framework.

::: gradual.base

### gradual.configs

Configuration management and validation.

::: gradual.configs

### gradual.constants

Framework constants and enumerations.

::: gradual.constants

### gradual.exceptions

Custom exception classes.

::: gradual.exceptions

### gradual.reporting

Reporting and metrics collection.

::: gradual.reporting

### gradual.runners

Test execution and load generation.

::: gradual.runners

## Quick API Examples

### Basic Test Execution

```python
from gradual.runners import TestRunner
from gradual.configs import ConfigManager

# Load configuration
config = ConfigManager("test_config.yaml")
runner = TestRunner(config)

# Run test
results = runner.run()
```

### Custom Protocol Handler

```python
from gradual.base import BaseProtocolHandler

class CustomHandler(BaseProtocolHandler):
    def execute_request(self, request_data):
        # Custom implementation
        pass

# Register handler
runner.register_protocol("custom", CustomHandler)
```

### Custom Assertions

```python
from gradual.base import BaseAssertion

class CustomAssertion(BaseAssertion):
    def validate(self, response):
        # Custom validation logic
        return True

# Use in test configuration
scenario = {
    "assertions": [
        {"type": "custom", "config": {...}}
    ]
}
```

## Configuration Schema

### Test Configuration

```yaml
name: "Test Name"
description: "Test Description"

target:
  base_url: "https://api.example.com"
  protocol: "http"
  timeout: 30
  verify_ssl: true

scenarios:
  - name: "Scenario Name"
    weight: 100
    steps:
      - request:
          method: "GET"
          path: "/endpoint"
        assertions:
          - status_code: 200

load:
  users: 100
  duration: 300
  ramp_up: 60
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GRADUAL_TARGET_URL` | Override target URL | None |
| `GRADUAL_TIMEOUT` | Request timeout | 30 |
| `GRADUAL_VERIFY_SSL` | SSL verification | true |
| `GRADUAL_LOG_LEVEL` | Logging level | INFO |

## Error Handling

The framework provides comprehensive error handling:

```python
from gradual.exceptions import (
    ConfigurationError,
    ExecutionError,
    ValidationError
)

try:
    runner.run()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except ExecutionError as e:
    print(f"Execution error: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Performance Monitoring

### Built-in Metrics

- Response time (min, max, average, percentiles)
- Throughput (requests per second)
- Error rate and types
- Resource usage (CPU, memory, network)

### Custom Metrics

```python
from gradual.reporting import MetricsCollector

class CustomMetrics(MetricsCollector):
    def collect(self):
        return {
            "custom_metric": self.calculate_metric()
        }

# Register custom metrics
runner.register_metrics(CustomMetrics())
```

## Extension Points

### Protocol Handlers

Implement `BaseProtocolHandler` to support new protocols:

```python
class CustomProtocolHandler(BaseProtocolHandler):
    def __init__(self, config):
        super().__init__(config)
    
    def execute_request(self, request_data):
        # Implementation
        pass
    
    def validate_response(self, response):
        # Implementation
        pass
    
    def cleanup(self):
        # Implementation
        pass
```

### Data Providers

Implement `BaseDataProvider` for custom data sources:

```python
class CustomDataProvider(BaseDataProvider):
    def __init__(self, config):
        super().__init__(config)
    
    def get_data(self):
        # Return data
        pass
    
    def cleanup(self):
        # Cleanup resources
        pass
```

### Assertions

Implement `BaseAssertion` for custom validations:

```python
class CustomAssertion(BaseAssertion):
    def __init__(self, config):
        super().__init__(config)
    
    def validate(self, response):
        # Validation logic
        return True
```

## Best Practices

### Performance

1. **Connection Pooling**: Reuse connections when possible
2. **Resource Management**: Implement proper cleanup methods
3. **Memory Efficiency**: Use generators for large datasets
4. **Concurrency**: Leverage gevent for I/O operations

### Reliability

1. **Error Handling**: Implement comprehensive error handling
2. **Retry Logic**: Add retry mechanisms for transient failures
3. **Circuit Breakers**: Implement circuit breakers for failing services
4. **Monitoring**: Add health checks and monitoring

### Extensibility

1. **Interface Design**: Follow established patterns
2. **Configuration**: Use flexible configuration schemas
3. **Documentation**: Document all public APIs
4. **Testing**: Maintain high test coverage

## Migration Guide

### From Previous Versions

When upgrading between major versions:

1. **Review Changes**: Check the changelog for breaking changes
2. **Update Configuration**: Update configuration files to new schema
3. **Test Extensions**: Verify custom extensions still work
4. **Update Dependencies**: Update any dependent code

### Configuration Migration

```python
# Old format
config = {
    "target_url": "https://api.example.com",
    "max_users": 100
}

# New format
config = {
    "target": {
        "base_url": "https://api.example.com"
    },
    "load": {
        "users": 100
    }
}
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Check virtual environment and dependencies
2. **Configuration Errors**: Validate YAML syntax and schema
3. **Performance Issues**: Monitor resource usage and bottlenecks
4. **Memory Issues**: Implement proper cleanup and resource management

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
runner.run(verbose=True)
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile execution
profiler = cProfile.Profile()
profiler.enable()

runner.run()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(20)
```

## Support and Community

- **Documentation**: This API reference and user guides
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Contributing**: See the development guide for contribution guidelines
