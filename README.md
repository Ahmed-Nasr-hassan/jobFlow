# JobFlow

A production-grade Python library for executing Python scripts in different environments with streaming log support, built using **Clean Architecture**, **SOLID principles**, and modern design patterns.

## Quick Start

```bash
# Install from source
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

```python
from jobflow import RunScriptUseCase, ScriptConfig, LocalSubprocessExecutor, StdoutLogSink

executor = LocalSubprocessExecutor()
log_sink = StdoutLogSink()
use_case = RunScriptUseCase(executor=executor, log_sink=log_sink)

config = ScriptConfig(script_path="script.py")
result = use_case.execute(config)
```

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed installation instructions
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started quickly
- **[Architecture Documentation](docs/ARCHITECTURE.md)** - Architecture overview
- **[Architecture Diagrams](docs/architecture.puml)** - Visual architecture diagrams
- **[Execution Flow](docs/execution-flow.puml)** - Sequence diagrams
- **[Design Patterns](docs/design-patterns.puml)** - Design pattern visualizations

## Features

- ✅ **Multiple Execution Environments** - Local, Lambda, Worker
- ✅ **Streaming Logs** - SSE, stdout, multiple sinks
- ✅ **File Access** - Local, S3, HTTP/HTTPS URLs
- ✅ **Bidirectional File Operations** - Download inputs, upload outputs
- ✅ **Framework Agnostic** - No framework dependencies in core
- ✅ **Clean Architecture** - SOLID principles, testable, extensible
- ✅ **Type Safe** - Full type hints (Python 3.11+)

## License

MIT License - See [LICENSE](LICENSE) file for details.
