"""README.md exporter for target projects - Production-level documentation generator."""

from pathlib import Path
from typing import Optional

from ..models import CodebaseAnalysis


class ReadmeExporter:
    """Exports production-level project README.md based on analysis results."""
    
    def __init__(self, analysis: CodebaseAnalysis):
        self.analysis = analysis
    
    def export(self, output_path: Path) -> None:
        """Export project README.md file."""
        readme_content = self._generate_production_readme()
        output_path.write_text(readme_content, encoding='utf-8')
    
    def _generate_production_readme(self) -> str:
        """Generate production-level README with comprehensive sections."""
        project_name = self.analysis.root_path.name
        
        # Prepare all context
        context = self._prepare_comprehensive_context()
        
        return f"""# {project_name}

{self._generate_badges()}

{self._generate_tagline(context)}

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
  - [Setup](#setup)
  - [Running Tests](#running-tests)
  - [Code Style](#code-style)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

## 🎯 About

{self._generate_detailed_about(context)}

### Built With

{self._generate_tech_stack(context)}

## ✨ Features

{self._generate_detailed_features(context)}

## 🚀 Getting Started

{self._generate_getting_started(context)}

### Prerequisites

{self._generate_prerequisites(context)}

### Installation

{self._generate_detailed_installation(context)}

## 💻 Usage

### Basic Usage

{self._generate_basic_usage(context)}

### Advanced Usage

{self._generate_advanced_usage(context)}

## 📁 Project Structure

{self._generate_detailed_structure(context)}

## 🏗️ Architecture

{self._generate_detailed_architecture(context)}

## 📚 API Documentation

{self._generate_api_docs(context)}

## ⚙️ Configuration

{self._generate_configuration(context)}

## 🛠️ Development

### Setup

{self._generate_dev_setup(context)}

### Running Tests

{self._generate_testing_info(context)}

### Code Style

{self._generate_code_style(context)}

## 🚢 Deployment

{self._generate_deployment_info(context)}

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📧 Contact

Project Link: [https://github.com/yourusername/{project_name}](https://github.com/yourusername/{project_name})

## 🙏 Acknowledgments

{self._generate_acknowledgments(context)}

---

**Note**: This README was automatically generated using [codebase-digest](https://github.com/codebase-digest/codebase-digest). For more detailed technical documentation, see the `.digest/` directory.
"""
    
    def _prepare_comprehensive_context(self) -> dict:
        """Prepare comprehensive context for README generation."""
        # Analyze imports
        imports = set(imp.module.split('.')[0] for imp in self.analysis.imports)
        stdlib = {'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing', 'dataclasses', 're', 'collections', 'abc', 'enum', 'functools', 'itertools'}
        external_deps = imports - stdlib
        
        # Detect frameworks and libraries
        frameworks = []
        if 'flask' in imports:
            frameworks.append(('Flask', 'Web framework'))
        if 'django' in imports:
            frameworks.append(('Django', 'Web framework'))
        if 'fastapi' in imports:
            frameworks.append(('FastAPI', 'Modern web framework'))
        if 'torch' in imports:
            frameworks.append(('PyTorch', 'Deep learning'))
        if 'tensorflow' in imports:
            frameworks.append(('TensorFlow', 'Machine learning'))
        if 'sklearn' in imports:
            frameworks.append(('scikit-learn', 'Machine learning'))
        if 'pandas' in imports:
            frameworks.append(('pandas', 'Data analysis'))
        if 'numpy' in imports:
            frameworks.append(('NumPy', 'Numerical computing'))
        if 'sqlalchemy' in imports:
            frameworks.append(('SQLAlchemy', 'Database ORM'))
        
        # Detect project type
        project_type = 'application'
        if any(fw[0] in ['Flask', 'Django', 'FastAPI'] for fw in frameworks):
            project_type = 'web_api'
        elif any(fw[0] in ['PyTorch', 'TensorFlow', 'scikit-learn'] for fw in frameworks):
            project_type = 'ml'
        elif 'pandas' in imports or 'numpy' in imports:
            project_type = 'data'
        
        # Get main classes and functions
        classes = [s for s in self.analysis.symbols if s.type == 'class']
        functions = [s for s in self.analysis.symbols if s.type == 'function' and not s.name.startswith('_')]
        
        # Get domain entities
        entities = self.analysis.domain_entities
        
        return {
            'imports': imports,
            'external_deps': external_deps,
            'frameworks': frameworks,
            'project_type': project_type,
            'classes': classes,
            'functions': functions,
            'entities': entities,
            'files': self.analysis.total_files,
            'lines': self.analysis.total_lines,
            'entry_points': self.analysis.entry_points,
            'flows': self.analysis.execution_flows
        }
    
    def _generate_badges(self) -> str:
        """Generate GitHub-style badges."""
        return f"""[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
"""
    
    def _generate_tagline(self, context: dict) -> str:
        """Generate a compelling tagline."""
        if context['project_type'] == 'web_api':
            return "A modern, scalable web API built with Python for high-performance applications."
        elif context['project_type'] == 'ml':
            return "A machine learning solution leveraging state-of-the-art algorithms for intelligent data processing."
        elif context['project_type'] == 'data':
            return "A powerful data processing and analysis toolkit for extracting insights from complex datasets."
        else:
            return f"A Python application with {context['files']} modules and {context['lines']:,} lines of production-ready code."
    
    def _generate_detailed_about(self, context: dict) -> str:
        """Generate detailed about section."""
        about = f"This project is a comprehensive {context['project_type'].replace('_', ' ')} solution "
        
        if context['entities']:
            entity_names = [e.name for e in context['entities'][:3]]
            about += f"that manages {', '.join(entity_names)}"
            if len(context['entities']) > 3:
                about += f" and {len(context['entities']) - 3} more domain entities"
            about += ". "
        
        about += f"\n\nThe system consists of:\n"
        about += f"- **{len(context['classes'])} classes** providing object-oriented architecture\n"
        about += f"- **{len(context['functions'])} functions** implementing core business logic\n"
        about += f"- **{context['files']} modules** organized for maintainability\n"
        about += f"- **{context['lines']:,} lines** of well-documented code\n"
        
        if context['flows']:
            about += f"\nThe application implements {len(context['flows'])} execution flows for different operational scenarios."
        
        return about
    
    def _generate_tech_stack(self, context: dict) -> str:
        """Generate technology stack list."""
        stack = []
        
        # Add Python
        stack.append("- [Python](https://www.python.org/) - Core programming language")
        
        # Add frameworks
        for framework, description in context['frameworks']:
            stack.append(f"- [{framework}](https://pypi.org/) - {description}")
        
        # Add other notable dependencies
        if 'requests' in context['imports']:
            stack.append("- [Requests](https://requests.readthedocs.io/) - HTTP library")
        if 'pydantic' in context['imports']:
            stack.append("- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation")
        
        return "\n".join(stack) if stack else "- Python 3.10+"
    
    def _generate_detailed_features(self, context: dict) -> str:
        """Generate detailed features list."""
        features = []
        
        # Analyze based on project type
        if context['project_type'] == 'web_api':
            features.append("### 🌐 Web API")
            features.append("- RESTful API endpoints with comprehensive documentation")
            features.append("- Request validation and error handling")
            features.append("- Authentication and authorization")
            features.append("- Rate limiting and security features")
        
        elif context['project_type'] == 'ml':
            features.append("### 🤖 Machine Learning")
            features.append("- Model training and evaluation pipelines")
            features.append("- Data preprocessing and feature engineering")
            features.append("- Model persistence and versioning")
            features.append("- Inference API for predictions")
        
        elif context['project_type'] == 'data':
            features.append("### 📊 Data Processing")
            features.append("- Efficient data loading and transformation")
            features.append("- Statistical analysis and visualization")
            features.append("- Data validation and quality checks")
            features.append("- Export to multiple formats")
        
        # Add entity-based features
        if context['entities']:
            features.append("\n### 💼 Business Logic")
            for entity in context['entities'][:5]:
                if entity.methods:
                    features.append(f"- **{entity.name}**: {', '.join(entity.methods[:3])}")
        
        # Add general features
        features.append("\n### 🔧 Technical Features")
        features.append(f"- Modular architecture with {len(context['classes'])} reusable components")
        features.append("- Comprehensive error handling and logging")
        features.append("- Type hints for better code quality")
        features.append("- Well-documented codebase")
        
        return "\n".join(features)
    
    def _generate_getting_started(self, context: dict) -> str:
        """Generate getting started section."""
        return f"""To get a local copy up and running, follow these simple steps.

This project requires Python 3.10 or higher and uses {len(context['external_deps'])} external dependencies."""
    
    def _generate_prerequisites(self, context: dict) -> str:
        """Generate prerequisites section."""
        prereqs = ["```bash\n# Ensure you have Python 3.10+ installed\npython --version\n"]
        
        if 'torch' in context['imports']:
            prereqs.append("\n# For GPU support (optional)\n# Install CUDA toolkit from NVIDIA")
        
        if any(fw[0] in ['Flask', 'Django', 'FastAPI'] for fw in context['frameworks']):
            prereqs.append("\n# For web development\n# Ensure you have a modern web browser")
        
        prereqs.append("```")
        return "".join(prereqs)
    
    def _generate_detailed_installation(self, context: dict) -> str:
        """Generate detailed installation instructions."""
        install = ["```bash\n# 1. Clone the repository\n"]
        install.append(f"git clone https://github.com/yourusername/{self.analysis.root_path.name}.git\n")
        install.append(f"cd {self.analysis.root_path.name}\n\n")
        
        install.append("# 2. Create a virtual environment\n")
        install.append("python -m venv venv\n\n")
        
        install.append("# 3. Activate the virtual environment\n")
        install.append("# On Windows:\nvenv\\Scripts\\activate\n")
        install.append("# On macOS/Linux:\nsource venv/bin/activate\n\n")
        
        install.append("# 4. Install dependencies\n")
        if context['external_deps']:
            install.append("pip install -r requirements.txt\n\n")
            install.append("# Or install manually:\n")
            for dep in sorted(list(context['external_deps']))[:8]:
                install.append(f"pip install {dep}\n")
        else:
            install.append("# No external dependencies required\n")
        
        install.append("```")
        return "".join(install)
    
    def _generate_basic_usage(self, context: dict) -> str:
        """Generate basic usage examples."""
        if not context['entry_points']:
            return "```bash\npython main.py\n```"
        
        main_entry = context['entry_points'][0]
        rel_path = main_entry.relative_to(self.analysis.root_path)
        
        usage = [f"```bash\n# Run the application\npython {rel_path}\n```\n\n"]
        
        # Add example based on project type
        if context['project_type'] == 'web_api':
            usage.append("The API will be available at `http://localhost:8000`\n\n")
            usage.append("```bash\n# Test the API\ncurl http://localhost:8000/api/health\n```")
        elif context['project_type'] == 'ml':
            usage.append("```python\n# Example: Train a model\nfrom train import train_model\n\n")
            usage.append("model = train_model(data_path='data/train.csv')\n```")
        
        return "".join(usage)
    
    def _generate_advanced_usage(self, context: dict) -> str:
        """Generate advanced usage examples."""
        advanced = []
        
        # Show main classes usage
        if context['classes']:
            advanced.append("```python\n# Import main components\n")
            for cls in context['classes'][:3]:
                advanced.append(f"from {cls.file_path.stem} import {cls.name}\n")
            advanced.append("\n# Initialize and use\n")
            if context['classes']:
                cls = context['classes'][0]
                advanced.append(f"{cls.name.lower()} = {cls.name}()\n")
            advanced.append("```")
        
        return "".join(advanced) if advanced else "See the [API Documentation](#api-documentation) for advanced usage patterns."
    
    def _generate_detailed_structure(self, context: dict) -> str:
        """Generate detailed project structure."""
        files = set()
        for symbol in self.analysis.symbols:
            rel_path = symbol.file_path.relative_to(self.analysis.root_path)
            files.add(str(rel_path))
        
        structure = [f"```\n{self.analysis.root_path.name}/\n"]
        structure.append("├── README.md              # This file\n")
        structure.append("├── requirements.txt       # Python dependencies\n")
        structure.append("├── .gitignore            # Git ignore rules\n")
        structure.append("├── LICENSE               # License file\n")
        
        for file_path in sorted(list(files))[:15]:
            file_name = Path(file_path).name
            if file_name in ['main.py', 'app.py', '__main__.py']:
                structure.append(f"├── {file_name}          # Application entry point\n")
            elif 'model' in file_name.lower():
                structure.append(f"├── {file_name}        # Data models and entities\n")
            elif 'service' in file_name.lower():
                structure.append(f"├── {file_name}      # Business logic layer\n")
            elif 'api' in file_name.lower() or 'route' in file_name.lower():
                structure.append(f"├── {file_name}         # API endpoints\n")
            elif 'config' in file_name.lower():
                structure.append(f"├── {file_name}      # Configuration management\n")
            elif 'util' in file_name.lower():
                structure.append(f"├── {file_name}        # Utility functions\n")
            elif 'test' in file_name.lower():
                structure.append(f"├── {file_name}        # Test suite\n")
            else:
                structure.append(f"├── {file_name}\n")
        
        if len(files) > 15:
            structure.append(f"└── ... and {len(files) - 15} more files\n")
        
        structure.append("```")
        return "".join(structure)
    
    def _generate_detailed_architecture(self, context: dict) -> str:
        """Generate detailed architecture description."""
        arch = ["### System Architecture\n\n"]
        
        if context['project_type'] == 'web_api':
            arch.append("```\nClient → API Layer → Business Logic → Data Layer → Database\n```\n\n")
        elif context['project_type'] == 'ml':
            arch.append("```\nData Input → Preprocessing → Model → Inference → Output\n```\n\n")
        else:
            arch.append("```\nInput → Processing → Business Logic → Output\n```\n\n")
        
        arch.append("### Components\n\n")
        arch.append(f"- **{len(context['classes'])} Classes**: Object-oriented components\n")
        arch.append(f"- **{len(context['functions'])} Functions**: Functional utilities\n")
        arch.append(f"- **{len(self.analysis.call_relations)} Interactions**: Component relationships\n")
        
        if context['flows']:
            arch.append("\n### Execution Flows\n\n")
            for flow in context['flows'][:3]:
                arch.append(f"**{flow.name}**: {flow.description}\n\n")
        
        return "".join(arch)
    
    def _generate_api_docs(self, context: dict) -> str:
        """Generate API documentation section."""
        if not context['classes']:
            return "API documentation is available in the source code docstrings."
        
        docs = ["### Main Classes\n\n"]
        for cls in context['classes'][:5]:
            docs.append(f"#### `{cls.name}`\n\n")
            if cls.docstring:
                docs.append(f"{cls.docstring.split(chr(10))[0]}\n\n")
            
            # Get methods from entities
            entity = next((e for e in context['entities'] if e.name == cls.name), None)
            if entity and entity.methods:
                docs.append("**Methods:**\n")
                for method in entity.methods[:5]:
                    docs.append(f"- `{method}()`\n")
                docs.append("\n")
        
        return "".join(docs)
    
    def _generate_configuration(self, context: dict) -> str:
        """Generate configuration section."""
        config = ["Configuration can be managed through:\n\n"]
        config.append("- Environment variables\n")
        config.append("- Configuration files\n")
        config.append("- Command-line arguments\n\n")
        
        config.append("```bash\n# Example environment variables\n")
        if context['project_type'] == 'web_api':
            config.append("export API_HOST=0.0.0.0\n")
            config.append("export API_PORT=8000\n")
            config.append("export DEBUG=False\n")
        else:
            config.append("export DEBUG=False\n")
            config.append("export LOG_LEVEL=INFO\n")
        config.append("```")
        
        return "".join(config)
    
    def _generate_dev_setup(self, context: dict) -> str:
        """Generate development setup instructions."""
        setup = ["```bash\n# Install development dependencies\n"]
        setup.append("pip install -e .[dev]\n\n")
        setup.append("# Install pre-commit hooks\n")
        setup.append("pre-commit install\n")
        setup.append("```")
        return "".join(setup)
    
    def _generate_testing_info(self, context: dict) -> str:
        """Generate testing information."""
        return """```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_module.py
```"""
    
    def _generate_code_style(self, context: dict) -> str:
        """Generate code style information."""
        style = ["This project follows PEP 8 style guidelines.\n\n"]
        style.append("```bash\n# Format code\nblack .\n\n")
        style.append("# Sort imports\nisort .\n\n")
        style.append("# Type checking\nmypy .\n")
        style.append("```")
        return "".join(style)
    
    def _generate_deployment_info(self, context: dict) -> str:
        """Generate deployment information."""
        if context['project_type'] == 'web_api':
            return """### Docker Deployment

```bash
# Build Docker image
docker build -t app-name .

# Run container
docker run -p 8000:8000 app-name
```

### Cloud Deployment

This application can be deployed to:
- AWS (EC2, ECS, Lambda)
- Google Cloud Platform
- Azure
- Heroku"""
        else:
            return """This application can be packaged and distributed using:

```bash
# Build distribution
python -m build

# Install from wheel
pip install dist/*.whl
```"""
    
    def _generate_acknowledgments(self, context: dict) -> str:
        """Generate acknowledgments section."""
        acks = []
        for framework, _ in context['frameworks']:
            acks.append(f"- [{framework}](https://pypi.org/) - Core framework")
        
        if not acks:
            acks.append("- Python Community - For excellent tools and libraries")
        
        return "\n".join(acks) if acks else "- Python Community - For excellent tools and libraries"
