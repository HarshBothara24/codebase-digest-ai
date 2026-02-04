"""README.md exporter for target projects."""

from pathlib import Path
from typing import List

from ..models import CodebaseAnalysis


class ReadmeExporter:
    """Exports project README.md based on analysis results."""
    
    def __init__(self, analysis: CodebaseAnalysis):
        self.analysis = analysis
    
    def export(self, output_path: Path) -> None:
        """Export project README.md file."""
        readme_content = self._generate_readme()
        output_path.write_text(readme_content, encoding='utf-8')
    
    def _generate_readme(self) -> str:
        """Generate complete project README.md."""
        return f"""# Project Overview

{self._generate_project_description()}

## Architecture

{self._generate_architecture_description()}

## Execution Flow

{self._generate_execution_flow_description()}

## Core Components

{self._generate_core_components()}

## Project Structure

{self._generate_project_structure()}

## How To Run

{self._generate_run_instructions()}

## Generated Artifacts

{self._generate_artifacts_description()}

## Development Notes

{self._generate_development_notes()}

## Future Improvements

{self._generate_future_improvements()}
"""
    
    def _generate_project_description(self) -> str:
        """Generate high-level project description based on domain entities and structure."""
        # Infer project type from domain entities and structure
        entity_names = [entity.name.lower() for entity in self.analysis.domain_entities]
        
        # Check for common patterns
        if any(name in entity_names for name in ['user', 'payment', 'wallet', 'account']):
            project_type = "financial services application"
            description = "that provides user management, payment processing, and digital wallet functionality"
        elif any(name in entity_names for name in ['product', 'order', 'cart', 'inventory']):
            project_type = "e-commerce application"
            description = "that handles product catalog, order management, and inventory tracking"
        elif any(name in entity_names for name in ['post', 'comment', 'user', 'article']):
            project_type = "content management system"
            description = "that manages articles, user interactions, and content publishing"
        elif any(name in entity_names for name in ['task', 'project', 'user', 'team']):
            project_type = "project management application"
            description = "that handles task tracking, project coordination, and team collaboration"
        else:
            # Generic description based on structure
            if len(self.analysis.domain_entities) > 0:
                project_type = "business application"
                description = f"built with {len(self.analysis.domain_entities)} core domain entities and service-oriented architecture"
            else:
                project_type = "software application"
                description = f"containing {len(self.analysis.symbols)} components across {len(self.analysis.languages)} programming languages"
        
        return f"This is a {project_type} {description}. The system is built with a {'service-oriented' if self._has_service_pattern() else 'modular'} architecture using {self._get_primary_language()} {'dataclasses for domain modeling and separate service layers for business logic' if self._has_service_pattern() else 'for implementation'}."
    
    def _generate_architecture_description(self) -> str:
        """Generate architecture description based on actual code structure."""
        # Analyze file structure to determine architecture
        files_by_name = {f.name: f for f in self.analysis.entry_points}
        has_models = any('model' in str(f).lower() for f in files_by_name)
        has_services = any('service' in str(f).lower() for f in files_by_name)
        has_controllers = any('controller' in str(f).lower() or 'view' in str(f).lower() for f in files_by_name)
        
        if has_models and has_services:
            return """The application follows a layered architecture with clear separation of concerns:

- **Domain Layer**: Contains core business entities with their associated behaviors
- **Service Layer**: Implements business logic through dedicated service classes
- **Application Layer**: Handles application bootstrapping, configuration, and orchestration

The system uses dependency injection patterns where components are coordinated to provide a cohesive platform."""
        else:
            return f"""The application follows a modular architecture with {len(self.analysis.symbols)} defined symbols and {len(self.analysis.call_relations)} call relationships.

Key architectural elements:
- **Functions:** {len([s for s in self.analysis.symbols if s.type == 'function'])}
- **Classes:** {len([s for s in self.analysis.symbols if s.type == 'class'])}
- **Methods:** {len([s for s in self.analysis.symbols if s.type == 'method'])}"""
    
    def _generate_execution_flow_description(self) -> str:
        """Generate execution flow description based on detected flows."""
        if not self.analysis.execution_flows:
            return "The application execution flow has not been fully analyzed. Please refer to the main entry points for startup sequence."
        
        main_flow = None
        for flow in self.analysis.execution_flows:
            if 'main' in flow.name.lower() or flow.entry_point == 'main':
                main_flow = flow
                break
        
        if main_flow:
            steps_description = " → ".join(main_flow.steps[:4])
            if len(main_flow.steps) > 4:
                steps_description += " → ..."
            
            return f"""The application starts through the `{main_flow.entry_point}()` function which follows this sequence:

{steps_description}

The runtime execution involves {len(self.analysis.execution_flows)} major flows including startup, core business operations, and data processing."""
        else:
            return f"The application implements {len(self.analysis.execution_flows)} execution flows for different operational scenarios. The main entry points handle initialization, business logic execution, and system coordination."
    
    def _generate_core_components(self) -> str:
        """Generate core components description."""
        content = ""
        
        # Domain Models
        domain_entities = self.analysis.domain_entities
        if domain_entities:
            content += "### Domain Models\n\n"
            for entity in domain_entities[:5]:  # Limit to top 5
                content += f"- **{entity.name}**: "
                if entity.fields:
                    content += f"Manages {', '.join(entity.fields[:3])}{'...' if len(entity.fields) > 3 else ''}"
                if entity.methods:
                    content += f"\n  - Methods: {', '.join([f'`{m}()`' for m in entity.methods[:3]])}"
                content += "\n\n"
        
        # Service Classes (if detected)
        service_classes = [s for s in self.analysis.symbols if s.type == 'class' and 'service' in s.name.lower()]
        if service_classes:
            content += "### Service Classes\n\n"
            for service in service_classes[:5]:
                content += f"- **{service.name}**: "
                # Try to infer responsibility from name
                if 'user' in service.name.lower():
                    content += "User lifecycle management, authentication, and CRUD operations"
                elif 'payment' in service.name.lower():
                    content += "Payment creation, processing, and retrieval"
                elif 'wallet' in service.name.lower():
                    content += "Wallet management and fund transfers"
                else:
                    content += f"Business logic implementation for {service.name.replace('Service', '').lower()} operations"
                content += "\n"
        
        return content if content else "Core components are organized as functions and classes providing the main application functionality."
    
    def _generate_project_structure(self) -> str:
        """Generate project structure description."""
        # Get main files
        main_files = []
        for entry_point in self.analysis.entry_points:
            rel_path = entry_point.relative_to(self.analysis.root_path)
            main_files.append(str(rel_path))
        
        # Add other important files based on symbols
        important_files = set()
        for symbol in self.analysis.symbols:
            rel_path = symbol.file_path.relative_to(self.analysis.root_path)
            important_files.add(str(rel_path))
        
        structure = f"```\n{self.analysis.root_path.name}/\n"
        for file_path in sorted(list(important_files)[:8]):  # Limit to 8 files
            file_name = Path(file_path).name
            if 'main' in file_name.lower():
                structure += f"├── {file_name}          # Application entry point and configuration\n"
            elif 'model' in file_name.lower():
                structure += f"├── {file_name}        # Domain entities and business objects\n"
            elif 'service' in file_name.lower():
                structure += f"├── {file_name}      # Business logic and service implementations\n"
            elif file_name == '__init__.py':
                structure += f"└── {file_name}      # Package initialization\n"
            else:
                structure += f"├── {file_name}\n"
        structure += "```"
        
        return structure
    
    def _generate_run_instructions(self) -> str:
        """Generate run instructions based on entry points."""
        if self.analysis.entry_points:
            main_entry = self.analysis.entry_points[0]
            rel_path = main_entry.relative_to(self.analysis.root_path)
            
            if str(rel_path) == 'main.py':
                return """Execute the application using:

```bash
python main.py
```

The application will initialize the configuration, set up database connections, and start the web server."""
            else:
                return f"""Execute the application using:

```bash
python {rel_path}
```

This will start the main application process."""
        else:
            return "Please refer to the project documentation for specific run instructions."
    
    def _generate_artifacts_description(self) -> str:
        """Generate description of analysis artifacts."""
        return """The following analysis artifacts provide insights into the codebase structure:

- **callgraph.html**: Interactive visualization showing function call relationships and execution flow from main entry points through service layers
- **report.html**: Comprehensive codebase analysis including metrics, complexity scores, and architectural overview
- **architecture.md**: Detailed breakdown of system components, domain entities, and execution flows
- **flows.md**: Documentation of identified execution paths including startup flow and business operations
- **ai-context.md**: Semantic understanding of the codebase optimized for AI-assisted development and maintenance"""
    
    def _generate_development_notes(self) -> str:
        """Generate development notes based on code patterns."""
        notes = []
        
        # Check for common patterns
        if self._has_service_pattern():
            notes.append("**Service Layer Pattern**: Business logic is encapsulated in dedicated service classes rather than being embedded in domain models")
        
        if self._has_dependency_injection():
            notes.append("**Dependency Injection**: Services are injected into components for better testability and modularity")
        
        if self._uses_dataclasses():
            notes.append("**Domain-Driven Design**: Core business concepts are modeled as first-class entities with their own behaviors")
        
        # Add language-specific notes
        if 'Python' in self.analysis.languages:
            notes.append("The system uses Python's `dataclass` decorator for clean domain modeling and leverages appropriate types for data handling")
        
        # Add architectural notes
        if len(self.analysis.execution_flows) > 2:
            notes.append(f"Key data flows include: {', '.join([flow.name.replace('_', ' ') for flow in self.analysis.execution_flows[:3]])}")
        
        content = "The application implements several key design patterns:\n\n"
        for note in notes:
            content += f"- {note}\n"
        
        return content
    
    def _generate_future_improvements(self) -> str:
        """Generate realistic future improvements."""
        improvements = []
        
        # Based on domain entities
        if any('payment' in entity.name.lower() for entity in self.analysis.domain_entities):
            improvements.append("**Event-Driven Architecture**: Implement domain events for payment processing and wallet transactions to enable better audit trails and integration with external systems")
        
        # Based on architecture
        if self._has_service_pattern():
            improvements.append("**API Layer**: Add REST API endpoints with proper authentication and authorization to expose the service functionality to external clients")
        
        # Generic improvements
        improvements.append("**Persistent Storage**: Integrate with a proper database system (PostgreSQL/MySQL) replacing any in-memory data structures with persistent storage and transaction support")
        
        content = ""
        for i, improvement in enumerate(improvements, 1):
            content += f"{i}. {improvement}\n\n"
        
        return content.rstrip()
    
    def _has_service_pattern(self) -> bool:
        """Check if the codebase uses service pattern."""
        return any('service' in symbol.name.lower() for symbol in self.analysis.symbols if symbol.type == 'class')
    
    def _has_dependency_injection(self) -> bool:
        """Check if the codebase uses dependency injection."""
        # Look for constructor parameters that are classes
        for symbol in self.analysis.symbols:
            if symbol.type == 'method' and symbol.name.endswith('.__init__') and len(symbol.parameters) > 2:
                return True
        return False
    
    def _uses_dataclasses(self) -> bool:
        """Check if the codebase uses dataclasses."""
        return any('dataclass' in symbol.decorators for symbol in self.analysis.symbols if symbol.decorators)
    
    def _get_primary_language(self) -> str:
        """Get the primary programming language."""
        if self.analysis.languages:
            return list(self.analysis.languages)[0]
        return "Python"