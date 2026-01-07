# JobFlow Architecture

## Overview

JobFlow follows **Clean Architecture** principles with strict dependency inversion. All dependencies point inward toward the domain layer.

## Layer Responsibilities

### 1. Domain Layer (`src/domain/`)

**Pure business logic - NO external dependencies**

- **Interfaces**: `ScriptExecutor`, `LogSink`
- **Value Objects**: `ScriptConfig`, `ExecutionResult`, `LogLevel`
- **Entities**: Domain models
- **Exceptions**: `DomainException`, `ScriptExecutionException`, `InvalidScriptException`

**Rules:**
- ✅ Can only depend on Python standard library
- ✅ No imports from application, infrastructure, or interfaces
- ✅ Defines contracts (interfaces) that infrastructure implements

### 2. Application Layer (`src/application/`)

**Use cases and orchestration**

- **Use Cases**: `RunScriptUseCase`
- Orchestrates script execution
- Handles lifecycle events
- Manages log streaming

**Rules:**
- ✅ Depends only on domain layer
- ✅ No infrastructure imports
- ✅ Contains business workflow logic

### 3. Infrastructure Layer (`src/infrastructure/`)

**Adapters that implement domain interfaces**

#### Executors (`src/infrastructure/executors/`)
- `LocalSubprocessExecutor` - Runs scripts as subprocesses
- `LambdaExecutor` - Runs scripts in-process (Lambda-style)
- `WorkerExecutor` - Stub for remote worker execution

#### Log Sinks (`src/infrastructure/logging/`)
- `StdoutLogSink` - Writes to stdout/stderr
- `SSELogSink` - Emits Server-Sent Events
- `CompositeLogSink` - Fan-out to multiple sinks

**Rules:**
- ✅ Implements domain interfaces
- ✅ Can use external libraries (subprocess, asyncio, etc.)
- ✅ No business logic

## Dependency Flow

```
Application → Domain ← Infrastructure
```

All dependencies point **inward** toward the domain.

## Design Patterns

### Strategy Pattern
- **Executors**: Different execution strategies (local, Lambda, worker)
- **Log Sinks**: Different logging strategies (stdout, SSE, file, etc.)

### Composite Pattern
- **CompositeLogSink**: Fan-out logs to multiple sinks

### Adapter Pattern
- Infrastructure adapters bridge external systems to domain interfaces

### Use Case Pattern
- `RunScriptUseCase` encapsulates execution workflow

## Extension Points

### Adding a New Executor

1. Create class in `src/infrastructure/executors/`
2. Implement `ScriptExecutor` interface
3. Register in `src/infrastructure/__init__.py`

### Adding a New Log Sink

1. Create class in `src/infrastructure/logging/`
2. Implement `LogSink` interface
3. Register in `src/infrastructure/__init__.py`

## Testing Strategy

- **Domain**: Unit tests with no mocks (pure logic)
- **Application**: Unit tests with mocked executors/log sinks
- **Infrastructure**: Integration tests with real subprocesses

## Key Principles

1. **Dependency Inversion**: High-level modules don't depend on low-level modules
2. **Interface Segregation**: Small, focused interfaces
3. **Single Responsibility**: Each class has one reason to change
4. **Open/Closed**: Open for extension, closed for modification
5. **Liskov Substitution**: Implementations are substitutable

