"""Main codebase analyzer that orchestrates parsing and analysis."""

import os
from pathlib import Path
from typing import Dict, List, Set

from ..models import CodebaseAnalysis
from ..parser import PythonParser, JavaScriptParser, BaseParser
from .flow_analyzer import FlowAnalyzer
from .metrics_analyzer import MetricsAnalyzer


class CodebaseAnalyzer:
    """Main analyzer that coordinates parsing and analysis of a codebase."""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.parsers: Dict[str, BaseParser] = {}
        self._register_parsers()
        
        # Ignore patterns
        self.ignore_patterns = {
            '__pycache__', '.git', '.svn', '.hg', 'node_modules',
            '.pytest_cache', '.mypy_cache', '.tox', 'venv', 'env',
            '.venv', 'dist', 'build', '*.egg-info', '.DS_Store'
        }
    
    def _register_parsers(self):
        """Register available parsers."""
        # Register parsers by extension without instantiating
        python_extensions = ['.py']
        js_extensions = ['.js', '.jsx', '.ts', '.tsx']
        
        for ext in python_extensions:
            self.parsers[ext] = PythonParser
        
        for ext in js_extensions:
            self.parsers[ext] = JavaScriptParser
    
    def analyze(self) -> CodebaseAnalysis:
        """Perform complete codebase analysis."""
        analysis = CodebaseAnalysis(root_path=self.root_path)
        
        # Find all relevant files
        files = self._find_source_files()
        analysis.total_files = len(files)
        
        # Parse each file
        for file_path in files:
            self._parse_file(file_path, analysis)
        
        # Detect entry points
        analysis.entry_points = self._detect_entry_points(files)
        
        # Analyze execution flows
        flow_analyzer = FlowAnalyzer(analysis)
        analysis.execution_flows = flow_analyzer.analyze_flows()
        
        # Calculate metrics
        metrics_analyzer = MetricsAnalyzer(analysis)
        analysis.total_lines = metrics_analyzer.count_total_lines(files)
        analysis.languages = metrics_analyzer.detect_languages(files)
        analysis.complexity_score = metrics_analyzer.calculate_complexity()
        
        # Build directory tree
        analysis.directory_tree = self._build_directory_tree()
        
        return analysis
    
    def _find_source_files(self) -> List[Path]:
        """Find all source files in the codebase."""
        files = []
        
        for root, dirs, filenames in os.walk(self.root_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for filename in filenames:
                file_path = Path(root) / filename
                if self._is_source_file(file_path) and not self._should_ignore(filename):
                    files.append(file_path)
        
        return files
    
    def _is_source_file(self, file_path: Path) -> bool:
        """Check if file is a source code file."""
        return file_path.suffix in self.parsers
    
    def _should_ignore(self, name: str) -> bool:
        """Check if file/directory should be ignored."""
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern or name.startswith(pattern):
                return True
        return False
    
    def _parse_file(self, file_path: Path, analysis: CodebaseAnalysis):
        """Parse a single file and add results to analysis."""
        parser_class = self.parsers.get(file_path.suffix)
        if not parser_class:
            return
        
        try:
            parser = parser_class(file_path)
            
            # Parse symbols
            symbols = parser.parse_symbols()
            analysis.symbols.extend(symbols)
            
            # Parse imports
            imports = parser.parse_imports()
            analysis.imports.extend(imports)
            
            # Parse calls
            calls = parser.parse_calls()
            analysis.call_relations.extend(calls)
            
            # Parse domain entities
            entities = parser.parse_domain_entities()
            analysis.domain_entities.extend(entities)
            
        except Exception as e:
            # Log error but continue processing
            print(f"Error parsing {file_path}: {e}")
    
    def _detect_entry_points(self, files: List[Path]) -> List[Path]:
        """Detect likely entry points in the codebase."""
        entry_points = []
        
        # Common entry point patterns
        entry_patterns = [
            'main.py', 'app.py', 'server.py', 'run.py', 'start.py',
            'manage.py', '__main__.py', 'wsgi.py', 'asgi.py',
            'index.js', 'server.js', 'app.js', 'main.js'
        ]
        
        for file_path in files:
            if file_path.name in entry_patterns:
                entry_points.append(file_path)
            elif file_path.name == '__init__.py':
                # Check if it's a package entry point
                if self._is_package_entry_point(file_path):
                    entry_points.append(file_path)
        
        return entry_points
    
    def _is_package_entry_point(self, init_file: Path) -> bool:
        """Check if __init__.py file is a package entry point."""
        try:
            content = init_file.read_text(encoding='utf-8')
            # Simple heuristic: contains main execution logic
            return 'if __name__' in content or 'main(' in content
        except:
            return False
    
    def _build_directory_tree(self) -> Dict:
        """Build a directory tree structure."""
        tree = {}
        
        for root, dirs, files in os.walk(self.root_path):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            rel_path = Path(root).relative_to(self.root_path)
            
            # Build nested structure
            current = tree
            for part in rel_path.parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add files
            source_files = [f for f in files 
                          if self._is_source_file(Path(root) / f) 
                          and not self._should_ignore(f)]
            
            if source_files:
                current['_files'] = source_files
        
        return tree