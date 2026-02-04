"""Metrics and statistics analyzer."""

from pathlib import Path
from typing import List, Set, Dict

from ..models import CodebaseAnalysis


class MetricsAnalyzer:
    """Analyzes codebase metrics and statistics."""
    
    def __init__(self, analysis: CodebaseAnalysis):
        self.analysis = analysis
    
    def count_total_lines(self, files: List[Path]) -> int:
        """Count total lines of code."""
        total_lines = 0
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += sum(1 for line in f if line.strip())
            except:
                continue
        
        return total_lines
    
    def detect_languages(self, files: List[Path]) -> Set[str]:
        """Detect programming languages in the codebase."""
        languages = set()
        
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala'
        }
        
        for file_path in files:
            lang = language_map.get(file_path.suffix)
            if lang:
                languages.add(lang)
        
        return languages
    
    def calculate_complexity(self) -> float:
        """Calculate a simple complexity score."""
        if not self.analysis.symbols:
            return 0.0
        
        # Simple complexity based on:
        # - Number of functions/classes
        # - Number of call relationships
        # - Depth of call chains
        
        symbol_count = len(self.analysis.symbols)
        call_count = len(self.analysis.call_relations)
        
        # Normalize to 0-100 scale
        base_complexity = min(100, (symbol_count + call_count) / 10)
        
        # Adjust for call chain depth
        max_chain_depth = self._calculate_max_call_depth()
        depth_factor = min(2.0, max_chain_depth / 5)
        
        return min(100.0, base_complexity * depth_factor)
    
    def _calculate_max_call_depth(self) -> int:
        """Calculate the maximum depth of call chains."""
        # Build a simple call graph
        call_graph = {}
        for call in self.analysis.call_relations:
            caller_name = call.caller_symbol.name
            if caller_name not in call_graph:
                call_graph[caller_name] = []
            call_graph[caller_name].append(call.callee_name)
        
        # Find maximum depth using DFS
        max_depth = 0
        
        def dfs(func: str, visited: Set[str], depth: int) -> int:
            if func in visited or func not in call_graph:
                return depth
            
            visited.add(func)
            local_max = depth
            
            for callee in call_graph[func]:
                local_max = max(local_max, dfs(callee, visited.copy(), depth + 1))
            
            return local_max
        
        for func in call_graph:
            max_depth = max(max_depth, dfs(func, set(), 0))
        
        return max_depth
    
    def get_file_statistics(self, files: List[Path]) -> Dict[str, int]:
        """Get detailed file statistics."""
        stats = {
            'total_files': len(files),
            'python_files': 0,
            'javascript_files': 0,
            'typescript_files': 0,
            'other_files': 0
        }
        
        for file_path in files:
            if file_path.suffix == '.py':
                stats['python_files'] += 1
            elif file_path.suffix in ['.js', '.jsx']:
                stats['javascript_files'] += 1
            elif file_path.suffix in ['.ts', '.tsx']:
                stats['typescript_files'] += 1
            else:
                stats['other_files'] += 1
        
        return stats