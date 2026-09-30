# Installation Guide

## Quick Install

```bash
# Install from current directory (development mode)
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Build Distribution Packages

```bash
# Install build tools
pip install build

# Build wheel and source distribution
python -m build

# Output files in dist/:
# - jobflow-0.1.0-py3-none-any.whl
# - jobflow-0.1.0.tar.gz
```

## Install from Built Distribution

```bash
# Install from wheel (recommended)
pip install dist/jobflow-0.1.0-py3-none-any.whl

# Or from source distribution
pip install dist/jobflow-0.1.0.tar.gz
```

## Verify Installation

```python
# Check installation
python -c "import jobflow; print(f'JobFlow {jobflow.__version__} installed')"

# Test imports
python -c "from jobflow import RunScriptUseCase, ScriptConfig; print('✓ All imports work')"
```

## Package Structure

After installation, the package structure is:

```
jobflow/                    # Root package (from src/__init__.py)
├── application/            # Use cases
├── domain/                # Business logic & interfaces
└── infrastructure/        # Adapters & implementations
    ├── executors/
    ├── file_providers/
    └── logging/
```

## Import Usage

All public APIs are available from the root package:

```python
# Recommended: Import from root package
from jobflow import (
    RunScriptUseCase,
    ScriptConfig,
    LocalSubprocessExecutor,
    StdoutLogSink,
)

# Or import from subpackages (also works)
from jobflow.application import RunScriptUseCase
from jobflow.domain import ScriptConfig
from jobflow.infrastructure import LocalSubprocessExecutor
```

## Development Setup

```bash
# Clone repository
git clone <repository-url>
cd jobFlow

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests (when tests are added)
pytest

# Format code
black src/

# Lint code
ruff check src/
```

## Publishing to PyPI (Future)

When ready to publish:

```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*

# Then users can install via:
pip install jobflow
```

