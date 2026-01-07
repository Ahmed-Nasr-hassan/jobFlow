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
from src.domain import ScriptConfig, FileRequirement
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

### File Access (Local, S3, URLs, etc.)

Scripts can access files from **any source** (local, S3, HTTP/HTTPS URLs) and files are automatically staged in the executor's context (local filesystem, Lambda /tmp, etc.):

```python
from src.domain import ScriptConfig, FileRequirement
from src.infrastructure import (
    LocalSubprocessExecutor,
    LambdaExecutor,
    LocalFileProvider,
    S3FileProvider,
    HTTPFileProvider,
    CompositeFileProvider,
)

# Create file providers for different sources
local_provider = LocalFileProvider()
s3_provider = S3FileProvider(bucket_name="my-bucket")
http_provider = HTTPFileProvider()

# Composite provider automatically routes based on source path format
composite_provider = CompositeFileProvider(local_provider, s3_provider, http_provider)

# Create executor with file provider
executor = LocalSubprocessExecutor(file_provider=composite_provider)

# Configure script with file requirements from ANY source
config = ScriptConfig(
    script_path="process_images.py",
    working_directory="/tmp/work",
    file_requirements=[
        FileRequirement(
            source="/data/input.csv",  # Local file
            destination="input.csv",  # Where script expects it
            required=True,
        ),
        FileRequirement(
            source="s3://my-bucket/images/photo1.jpg",  # S3 file
            destination="photo1.jpg",
            required=True,
        ),
        FileRequirement(
            source="https://example.com/images/photo2.jpg",  # HTTP URL
            destination="photo2.jpg",
            required=True,
        ),
        FileRequirement(
            source="https://cdn.example.com/config.json",  # Optional file
            destination="config.json",
            required=False,  # Won't fail if missing
        ),
    ],
)

# Files are automatically:
# 1. Downloaded from source (local/S3/URL)
# 2. Staged in executor's context (working_directory or /tmp for Lambda)
# 3. Available to script during execution
# 4. Uploaded to destinations after execution (if file_outputs specified)
# 5. Cleaned up after execution
result = use_case.execute(config)
```

### Bidirectional File Access (Download + Upload)

The library supports **dual interaction**: download input files AND upload output files:

```python
from src.domain import ScriptConfig, FileRequirement, FileOutput
from src.infrastructure import (
    LocalSubprocessExecutor,
    CompositeFileProvider,
    LocalFileProvider,
    S3FileProvider,
    HTTPFileProvider,
)

# Create composite provider
providers = CompositeFileProvider(
    LocalFileProvider(),
    S3FileProvider(bucket_name="my-bucket"),
    HTTPFileProvider(),
)

executor = LocalSubprocessExecutor(file_provider=providers)

# Configure with both inputs and outputs
config = ScriptConfig(
    script_path="process_images.py",
    working_directory="/tmp/work",
    # Download input files from any source
    file_requirements=[
        FileRequirement(
            source="https://example.com/input1.jpg",  # Download from URL
            destination="input1.jpg",
        ),
        FileRequirement(
            source="s3://bucket/input2.jpg",  # Download from S3
            destination="input2.jpg",
        ),
    ],
    # Upload output files to any destination
    file_outputs=[
        FileOutput(
            source="output1.jpg",  # File created by script
            destination="s3://bucket/results/output1.jpg",  # Upload to S3
            required=True,
        ),
        FileOutput(
            source="output2.jpg",
            destination="/backup/output2.jpg",  # Upload to local path
            required=False,  # Optional - won't fail if missing
        ),
        FileOutput(
            source="report.json",
            destination="https://api.example.com/upload",  # Upload to HTTP endpoint
            required=True,
        ),
    ],
)

# Complete workflow:
# 1. Downloads input files (URL → local, S3 → local)
# 2. Script executes and creates output files
# 3. Uploads output files (local → S3, local → HTTP, local → local)
# 4. Cleans up staged files
result = use_case.execute(config)
```

### Executor Context-Aware File Staging

Files are automatically staged in the executor's context:

- **LocalSubprocessExecutor**: Files staged to `working_directory` (or current directory)
- **LambdaExecutor**: Files staged to `/tmp` (Lambda's writable space) or `working_directory` if specified
- **WorkerExecutor**: Files staged according to worker's context

```python
# Lambda executor automatically uses /tmp for file staging
lambda_executor = LambdaExecutor(file_provider=composite_provider)

config = ScriptConfig(
    script_path="process.py",
    # working_directory not needed - defaults to /tmp in Lambda
    file_requirements=[
        FileRequirement(
            source="https://example.com/data.csv",  # Download from URL
            destination="data.csv",  # Available at /tmp/data.csv in Lambda
        ),
    ],
)
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
│   ├── file_provider.py # FileProvider interface
│   ├── logging.py       # LogSink interface
│   ├── models.py        # ExecutionResult, ScriptConfig, FileRequirement
│   └── exceptions.py    # Domain exceptions
│
├── application/         # Use cases
│   └── run_script.py    # RunScriptUseCase
│
└── infrastructure/      # Adapters
    ├── executors/       # Executor implementations
    ├── file_providers/   # File provider implementations
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

### Adding a New File Provider

```python
from src.domain import FileProvider
from pathlib import Path

class HTTPFileProvider(FileProvider):
    def get_file(self, source_path: str, destination_path: str) -> Path:
        # Download from HTTP/HTTPS URL
        import urllib.request
        urllib.request.urlretrieve(source_path, destination_path)
        return Path(destination_path)
    
    async def get_file_async(self, source_path: str, destination_path: str) -> Path:
        # Async download logic
        pass
    
    def cleanup(self, path: Path) -> None:
        # Clean up downloaded file
        path.unlink()
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
