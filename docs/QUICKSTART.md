# Quick Start Guide

## Installation

### Install from Source

```bash
# Clone or navigate to the project directory
cd jobFlow

# Install in editable/development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Verify Installation

```python
# Test the installation
python -c "import jobflow; print(f'JobFlow {jobflow.__version__} installed successfully')"
```

## Basic Usage

```python
from jobflow import (
    RunScriptUseCase,
    ScriptConfig,
    LocalSubprocessExecutor,
    StdoutLogSink,
)

# Create executor and log sink
executor = LocalSubprocessExecutor()
log_sink = StdoutLogSink()

# Create use case
use_case = RunScriptUseCase(executor=executor, log_sink=log_sink)

# Configure script
config = ScriptConfig(
    script_path="path/to/script.py",
    working_directory="/tmp",
)

# Execute
result = use_case.execute(config)
print(f"Status: {result.status.value}, Exit Code: {result.exit_code}")
```

## Building Distribution Packages

```bash
# Install build tools
pip install build

# Build wheel and source distribution
python -m build

# Output will be in dist/ directory:
# - jobflow-0.1.0-py3-none-any.whl
# - jobflow-0.1.0.tar.gz
```

## Installing from Built Distribution

```bash
# Install from wheel (recommended)
pip install dist/jobflow-0.1.0-py3-none-any.whl

# Or from source distribution
pip install dist/jobflow-0.1.0.tar.gz
```

## Package Structure After Installation

After installation, you can import everything from the root package:

```python
# All imports from root package
from jobflow import (
    # Application
    RunScriptUseCase,
    
    # Domain
    ScriptExecutor,
    FileProvider,
    LogSink,
    ScriptConfig,
    FileRequirement,
    FileOutput,
    ExecutionResult,
    
    # Infrastructure - Executors
    LocalSubprocessExecutor,
    LambdaExecutor,
    WorkerExecutor,
    
    # Infrastructure - File Providers
    LocalFileProvider,
    S3FileProvider,
    HTTPFileProvider,
    CompositeFileProvider,
    
    # Infrastructure - Log Sinks
    StdoutLogSink,
    SSELogSink,
    CompositeLogSink,
)
```

