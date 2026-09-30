# JobFlow Documentation

This directory contains all documentation and diagrams for the JobFlow library.

## Documentation Files

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete architecture documentation
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide

## Diagrams (PlantUML)

- **[architecture.puml](architecture.puml)** - Overall architecture diagram showing all layers and relationships
- **[execution-flow.puml](execution-flow.puml)** - Sequence diagram showing execution flow
- **[design-patterns.puml](design-patterns.puml)** - Design patterns used in the library

## Viewing PlantUML Diagrams

### VS Code
Install the "PlantUML" extension, then open any `.puml` file.

### Online
1. Copy the contents of a `.puml` file
2. Go to http://www.plantuml.com/plantuml/uml/
3. Paste and view

### Command Line
```bash
# Install PlantUML
# macOS: brew install plantuml
# Or download from: https://plantuml.com/download

# Generate PNG
plantuml architecture.puml

# Generate SVG
plantuml -tsvg architecture.puml
```

