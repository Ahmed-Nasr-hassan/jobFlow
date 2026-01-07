# JobFlow

A production-grade Python library for executing Python scripts in different environments with streaming log support, built using **Clean Architecture**, **SOLID principles**, and modern design patterns.

## 🏗️ Architecture

JobFlow follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│           Application Layer (Use Cases)                  │
│  RunScriptUseCase                                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Domain Layer (Business Rules)               │
│  ScriptExecutor, LogSink, ExecutionResult                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│         Infrastructure Layer (Adapters)                  │
│  Executors, Log Sinks                                    │
└─────────────────────────────────────────────────────────┘
```

### Key Principles

- **Domain Layer**: Pure business logic, no external dependencies
- **Application Layer**: Orchestrates use cases
- **Infrastructure Layer**: Implements domain interfaces (Strategy, Adapter patterns)

## 🚀 Features

- ✅ **Multiple Execution Environments**
  - Local subprocess execution
  - In-process execution (Lambda-style)
  - Remote worker execution (extensible)

- ✅ **Streaming Logs**
  - Server-Sent Events (SSE) support
  - Multiple log sinks (fan-out pattern)
  - Real-time log streaming

- ✅ **Framework Agnostic**
  - No FastAPI/Flask assumptions in core
  - No AWS dependencies in domain
  - Easy integration with any framework

- ✅ **Clean Architecture**
  - Dependency inversion
  - SOLID principles
  - Testable and extensible

- ✅ **Type Safe**
  - Full type hints (Python 3.11+)
  - Comprehensive docstrings

## 📦 Installation

```bash
pip install jobflow
```

Or install from source:

```bash
git clone https://github.com/your-org/jobflow.git
cd jobflow
pip install -e .
```

## 📖 Usage

### Basic Usage

```python
from src.application import RunScriptUseCase
from src.domain import ScriptConfig
from src.infrastructure import LocalSubprocessExecutor, StdoutLogSink

# Create executor and log sink
executor = LocalSubprocessExecutor()
log_sink = StdoutLogSink()

# Create use case
use_case = RunScriptUseCase(executor=executor, log_sink=log_sink)

# Configure script
config = ScriptConfig(
    script_path="path/to/script.py",
    working_directory="/tmp",
    environment_variables={"ENV": "production"},
    timeout_seconds=30,
)

# Execute
result = use_case.execute(config)

print(f"Status: {result.status.value}")
print(f"Exit Code: {result.exit_code}")
print(f"Duration: {result.duration_seconds:.2f}s")
```

### Async Execution with Streaming

```python
import asyncio
from src.application import RunScriptUseCase
from src.domain import ScriptConfig
from src.infrastructure import LocalSubprocessExecutor, StdoutLogSink

async def main():
    executor = LocalSubprocessExecutor()
    log_sink = StdoutLogSink()
    use_case = RunScriptUseCase(executor=executor, log_sink=log_sink)

    config = ScriptConfig(script_path="script.py")

    async for item in use_case.execute_async(config):
        if isinstance(item, str):
            print(f"Log: {item}")
        else:
            print(f"Result: {item.status.value}")

asyncio.run(main())
```

### Multiple Log Sinks (Fan-out)

```python
from src.infrastructure import (
    LocalSubprocessExecutor,
    StdoutLogSink,
    SSELogSink,
    CompositeLogSink,
)

# Create multiple sinks
stdout_sink = StdoutLogSink()

def send_sse(message: str):
    # Your SSE sending logic
    print(f"SSE: {message}")

sse_sink = SSELogSink(send_callback=send_sse)

# Composite sink forwards to all
composite_sink = CompositeLogSink(stdout_sink, sse_sink)

# Use composite sink
executor = LocalSubprocessExecutor()
use_case = RunScriptUseCase(executor=executor, log_sink=composite_sink)
```

### SSE Integration Example

For Server-Sent Events integration, use `SSELogSink` with a callback:

```python
import asyncio
from src.application import RunScriptUseCase
from src.domain import ScriptConfig
from src.infrastructure import LocalSubprocessExecutor, SSELogSink

async def main():
    executor = LocalSubprocessExecutor()
    
    # Create SSE log sink with callback
    sse_queue = asyncio.Queue()
    
    def send_sse(message: str):
        sse_queue.put_nowait(message)
    
    log_sink = SSELogSink(send_callback=send_sse)
    use_case = RunScriptUseCase(executor=executor, log_sink=log_sink)
    
    config = ScriptConfig(script_path="script.py")
    
    async for item in use_case.execute_async(config):
        if isinstance(item, str):
            # Process log message
            pass
        else:
            # Process final result
            pass
```

## 🧩 Design Patterns

### Strategy Pattern
- **Executors**: `LocalSubprocessExecutor`, `LambdaExecutor`, `WorkerExecutor`
- **Log Sinks**: `StdoutLogSink`, `SSELogSink`, custom sinks

### Composite Pattern
- **CompositeLogSink**: Fan-out logs to multiple sinks

### Adapter Pattern
- Infrastructure adapters implement domain interfaces

### Use Case Pattern
- `RunScriptUseCase` orchestrates execution

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## 📁 Project Structure

```
src/
├── domain/              # Pure business logic
│   ├── executor.py      # ScriptExecutor interface
│   ├── logging.py       # LogSink interface
│   ├── models.py        # ExecutionResult, ScriptConfig
│   └── exceptions.py    # Domain exceptions
│
├── application/         # Use cases
│   └── run_script.py    # RunScriptUseCase
│
└── infrastructure/      # Adapters
    ├── executors/       # Executor implementations
    └── logging/         # Log sink implementations
```

## 🔌 Extending the Library

### Adding a New Executor

```python
from src.domain import ScriptExecutor, ScriptConfig, ExecutionResult

class DockerExecutor(ScriptExecutor):
    def execute(self, config: ScriptConfig, log_sink=None) -> ExecutionResult:
        # Your Docker execution logic
        pass
    
    async def execute_async(self, config: ScriptConfig, log_sink=None):
        # Your async Docker execution logic
        async for item in ...:
            yield item
```

### Adding a New Log Sink

```python
from src.domain import LogSink, LogLevel

class KafkaLogSink(LogSink):
    def emit(self, level: LogLevel, message: str, metadata=None):
        # Send to Kafka
        pass
    
    def close(self):
        # Close Kafka connection
        pass
```

## 🎯 Design Decisions

1. **No Framework Dependencies in Core**: Domain and application layers are framework-agnostic
2. **Dependency Injection**: All dependencies injected via constructors
3. **Interface Segregation**: Small, focused interfaces
4. **Open/Closed Principle**: Easy to extend without modifying core
5. **Single Responsibility**: Each class has one clear purpose

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows Clean Architecture principles
- All tests pass
- Type hints are complete
- Docstrings are provided for public APIs

## 🔮 Roadmap

- [ ] Docker executor implementation
- [ ] Kubernetes executor implementation
- [ ] WebSocket log sink
- [ ] Kafka log sink
- [ ] File log sink
- [ ] Comprehensive test suite
- [ ] Performance benchmarks
