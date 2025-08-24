# API Reference

This page provides comprehensive API documentation for the gradual package.

## Available Modules

The following modules are automatically discovered and documented:

- [Base](base.md) - `gradual.base`
- [Configs](configs.md) - `gradual.configs`
- [Constants](constants.md) - `gradual.constants`
- [Exceptions](exceptions.md) - `gradual.exceptions`
- [Reporting](reporting.md) - `gradual.reporting`
- [Runners](runners.md) - `gradual.runners`
- [Parser](parser.md) - `gradual.configs.parser`
- [Phase](phase.md) - `gradual.configs.phase`
- [Request](request.md) - `gradual.configs.request`
- [Scenario](scenario.md) - `gradual.configs.scenario`
- [Validate](validate.md) - `gradual.configs.validate`
- [Orchestrator](orchestrator.md) - `gradual.base.orchestrator`
- [Request_Types](request_types.md) - `gradual.constants.request_types`
- [Adapters](adapters.md) - `gradual.reporting.adapters`
- [Logger](logger.md) - `gradual.reporting.logger`
- [Stats](stats.md) - `gradual.reporting.stats`
- [Base](base.md) - `gradual.reporting.adapters.base`
- [Logging](logging.md) - `gradual.reporting.adapters.logging`
- [Iterators](iterators.md) - `gradual.runners.iterators`
- [Phase](phase.md) - `gradual.runners.phase`
- [Request](request.md) - `gradual.runners.request`
- [Runner](runner.md) - `gradual.runners.runner`
- [Scenario](scenario.md) - `gradual.runners.scenario`
- [Session](session.md) - `gradual.runners.session`
- [Http](Http.md) - `gradual.runners.request.Http`
- [Socketio](SocketIO.md) - `gradual.runners.request.SocketIO`
- [Base](base.md) - `gradual.runners.request.base`


## Automatic Discovery

This documentation is automatically generated using a Python script that:
1. Discovers all modules in the package
2. Generates individual documentation files for each module
3. Uses mkdocstrings to extract documentation from docstrings
4. Updates automatically when you run the script

To regenerate all API documentation, run:
```bash
python generate_api_docs.py
```
