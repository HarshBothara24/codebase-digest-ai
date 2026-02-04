# codebase-digest

🚀 **AI-Native Code Intelligence Engine**

Transform any codebase into semantic architectural understanding, execution flows, and human-readable engineering reports.

## 🧱 What It Does

This is NOT a repo summarizer. This is a code intelligence engine that explains:
- **What this system does** - Infers project purpose from domain entities
- **How data flows** - Maps execution paths and call relationships  
- **Where logic lives** - Identifies core components and their responsibilities
- **What domains exist** - Detects business entities (User, Payment, Wallet, etc.)
- **What files matter** - Highlights entry points and key modules

## ✨ Features

- **🔍 Semantic Analysis**: Extract functions, classes, methods, and imports with full context
- **📊 Interactive Call Graphs**: Visualize function relationships and execution flows
- **🏗️ Domain Entity Detection**: Automatically identify core business objects
- **🔄 Execution Flow Mapping**: Trace request paths through the system
- **📋 Project README Generation**: Auto-generate documentation for new developers
- **📈 Multi-format Output**: HTML dashboards + Markdown reports + JSON data + Interactive graphs

## 🚀 Quick Start

```bash
# Install
pip install codebase-digest

# Analyze current directory
codebase-digest build

# Analyze specific directory  
codebase-digest build /path/to/project

# Generate with interactive call graph
codebase-digest build --graph

# Quick stats
codebase-digest stats

# Search for patterns
codebase-digest query "wallet"
```

## 📁 Output Structure

Generates `.digest/` directory with comprehensive analysis:
```
.digest/
├── README.md          # Project documentation for developers
├── callgraph.html     # Interactive call graph visualization
├── report.html        # Comprehensive HTML dashboard
├── architecture.md    # Technical architecture breakdown
├── flows.md           # Execution flow documentation
├── ai-context.md      # AI-optimized context file
└── entities.json      # Structured analysis data
```

## 📊 Example Output

For a Python financial services project:

```
📊 Codebase Statistics
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Total Files      ┃ 4      ┃
┃ Lines of Code    ┃ 189    ┃
┃ Languages        ┃ Python ┃
┃ Functions        ┃ 24     ┃
┃ Classes          ┃ 8      ┃
┃ Domain Entities  ┃ 7      ┃
┃ Execution Flows  ┃ 4      ┃
┃ Complexity Score ┃ 1.8    ┃
┗━━━━━━━━━━━━━━━━━━┻━━━━━━━━┛

Graph Stats: 29 nodes, 27 edges, 7 components
```

**Generated README.md excerpt:**
```markdown
# Project Overview

This is a financial services application that provides user management, 
payment processing, and digital wallet functionality. The system is built 
with a service-oriented architecture using Python dataclasses for domain 
modeling and separate service layers for business logic.

## Architecture

The application follows a layered architecture with clear separation of concerns:
- **Domain Layer**: Contains core business entities (User, Payment, Wallet)
- **Service Layer**: Implements business logic (UserService, PaymentService)  
- **Application Layer**: Handles bootstrapping and orchestration
```

## 💡 Commands

```bash
# Full analysis with all outputs
codebase-digest build [PATH]

# Specific formats
codebase-digest build --format html       # HTML dashboard only
codebase-digest build --format markdown   # Markdown reports only  
codebase-digest build --format json       # JSON data only

# Interactive call graph with depth filtering
codebase-digest build --graph --graph-depth 3

# Quick metrics and search
codebase-digest stats [PATH]              # Project statistics
codebase-digest query "search term" [PATH] # Search patterns
```

## 🎯 Key Features

### 🕸️ Interactive Call Graph
- **Probabilistic entrypoint detection** - Finds real execution starting points
- **Noise filtering** - Removes builtin calls and isolated nodes  
- **Depth filtering** - Focus on core execution spine
- **Professional UI** - GitHub/Linear/Notion inspired design

### 📝 Smart README Generation  
- **Project type inference** - Detects financial, e-commerce, CMS patterns
- **Architecture analysis** - Service-oriented vs modular detection
- **Run instructions** - Inferred from entry points
- **Future improvements** - Realistic enhancement suggestions

### 🔍 Semantic Understanding
- **Symbol-aware analysis** - True function-level relationships
- **Domain entity detection** - Business object identification
- **Execution flow mapping** - Startup and runtime sequences
- **Cross-file analysis** - Import and dependency tracking

## 🛠️ Tech Stack

- **Python 3.10+** - Core language
- **AST parsing** - Deep Python code analysis
- **NetworkX** - Call graph analysis and visualization
- **vis.js** - Interactive graph rendering
- **Typer** - CLI interface
- **Rich** - Beautiful terminal output

## 📋 Supported Languages

- ✅ **Python** - Full AST analysis with call graphs
- 🚧 **JavaScript/TypeScript** - Parser implemented, integration in progress
- 🚧 **Java** - Planned
- 🚧 **Go** - Planned

## 🎯 Use Cases

- **New Developer Onboarding** - Understand unfamiliar codebases quickly
- **Code Reviews** - Architectural overview and impact analysis  
- **Documentation Generation** - Auto-generate project documentation
- **Refactoring Planning** - Identify core components and dependencies
- **AI-Assisted Development** - Provide context for LLM code assistance

## 🔧 Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code  
black .
isort .

# Type checking
mypy codebase_digest/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built with modern Python tooling and best practices
- Inspired by professional developer tools (JetBrains, Sourcegraph)
- Designed for AI-native development workflows