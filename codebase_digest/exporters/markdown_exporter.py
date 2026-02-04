"""Markdown report exporter."""

from datetime import datetime
from pathlib import Path
from typing import Dict

from ..models import CodebaseAnalysis


class MarkdownExporter:
    """Exports analysis results to Markdown format."""
    
    def __init__(self, analysis: CodebaseAnalysis):
        self.analysis = analysis
    
    def export(self, output_path: Path) -> None:
        """Export analysis to Markdown file."""
        markdown_content = self._generate_markdown()
        output_path.write_text(markdown_content, encoding='utf-8')
    
    def _generate_markdown(self) -> str:
        """Generate complete Markdown report."""
        return f"""# {self.analysis.root_path.name}

**Codebase Analysis Report**

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📊 Summary

| Metric | Value |
|--------|-------|
| Total Files | {self.analysis.total_files} |
| Languages | {len(self.analysis.languages)} |
| Lines of Code | {self.analysis.total_lines:,} |
| Complexity Score | {self.analysis.complexity_score:.1f} |

{self._generate_overview()}

{self._generate_architecture()}

{self._generate_directory_structure()}

{self._generate_key_components()}

{self._generate_core_logic()}

{self._generate_dependencies()}

{self._generate_data_flow()}

{self._generate_risks()}

{self._generate_recommendations()}
"""
    
    def _generate_overview(self) -> str:
        """Generate overview section."""
        entry_points = [str(ep.relative_to(self.analysis.root_path)) for ep in self.analysis.entry_points]
        entry_points_str = ', '.join(entry_points) if entry_points else 'None detected'
        
        languages_badges = ' '.join(f'`{lang}`' for lang in sorted(self.analysis.languages))
        
        return f"""## 🚀 Overview

This codebase contains {self.analysis.total_files} files across {len(self.analysis.languages)} programming languages, with a total of {self.analysis.total_lines:,} lines of code.

### Entry Points
```
{entry_points_str}
```

### Languages
{languages_badges}
"""
    
    def _generate_architecture(self) -> str:
        """Generate architecture section."""
        function_count = len([s for s in self.analysis.symbols if s.type == 'function'])
        class_count = len([s for s in self.analysis.symbols if s.type == 'class'])
        method_count = len([s for s in self.analysis.symbols if s.type == 'method'])
        
        return f"""## 🧱 Architecture

The codebase follows a modular architecture with {len(self.analysis.symbols)} defined symbols and {len(self.analysis.call_relations)} call relationships.

### Key Statistics
- **Functions:** {function_count}
- **Classes:** {class_count}
- **Methods:** {method_count}
- **Domain Entities:** {len(self.analysis.domain_entities)}
"""
    
    def _generate_directory_structure(self) -> str:
        """Generate directory structure section."""
        tree_md = self._render_directory_tree(self.analysis.directory_tree)
        
        return f"""## 📁 Directory Structure

```
{self.analysis.root_path.name}/
{tree_md}
```
"""
    
    def _render_directory_tree(self, tree: Dict, prefix: str = "") -> str:
        """Render directory tree as Markdown."""
        if not tree:
            return ""
        
        lines = []
        items = list(tree.items())
        
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            
            if key == '_files':
                for j, file in enumerate(value):
                    file_is_last = j == len(value) - 1
                    file_prefix = "└── " if file_is_last else "├── "
                    lines.append(f"{prefix}{'    ' if is_last else '│   '}{file_prefix}{file}")
            else:
                lines.append(f"{prefix}{current_prefix}{key}/")
                if isinstance(value, dict):
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    lines.append(self._render_directory_tree(value, next_prefix))
        
        return "\n".join(filter(None, lines))
    
    def _generate_key_components(self) -> str:
        """Generate key components section."""
        if not self.analysis.symbols:
            return "## 🔧 Key Components\n\nNo components detected."
        
        # Group by type
        functions = [s for s in self.analysis.symbols if s.type == 'function'][:10]
        classes = [s for s in self.analysis.symbols if s.type == 'class'][:10]
        
        content = "## 🔧 Key Components\n\n"
        
        if functions:
            content += "### Functions\n"
            for func in functions:
                rel_path = func.file_path.relative_to(self.analysis.root_path)
                content += f"- `{func.name}()` - {rel_path}:{func.line_number}\n"
            content += "\n"
        
        if classes:
            content += "### Classes\n"
            for cls in classes:
                rel_path = cls.file_path.relative_to(self.analysis.root_path)
                content += f"- `{cls.name}` - {rel_path}:{cls.line_number}\n"
            content += "\n"
        
        return content
    
    def _generate_core_logic(self) -> str:
        """Generate core logic section."""
        if not self.analysis.execution_flows:
            return "## ⚡ Core Logic\n\nNo execution flows detected."
        
        content = f"## ⚡ Core Logic\n\nIdentified {len(self.analysis.execution_flows)} execution flows:\n\n"
        
        for flow in self.analysis.execution_flows:
            content += f"### {flow.name}\n"
            content += f"{flow.description}\n\n"
            
            if flow.steps:
                steps_str = " → ".join(flow.steps[:5])
                if len(flow.steps) > 5:
                    steps_str += f" ... (+{len(flow.steps) - 5} more)"
                content += f"```\n{steps_str}\n```\n\n"
        
        return content
    
    def _generate_dependencies(self) -> str:
        """Generate dependencies section."""
        if not self.analysis.imports:
            return "## 📦 Dependencies\n\nNo imports detected."
        
        # Group imports by module
        import_counts = {}
        for imp in self.analysis.imports:
            if imp.module not in import_counts:
                import_counts[imp.module] = 0
            import_counts[imp.module] += 1
        
        # Sort by frequency
        top_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        content = "## 📦 Dependencies\n\n### Top Imported Modules\n\n"
        content += "| Module | Import Count |\n"
        content += "|--------|-------------|\n"
        
        for module, count in top_imports:
            content += f"| `{module}` | {count} |\n"
        
        return content + "\n"
    
    def _generate_data_flow(self) -> str:
        """Generate data flow section."""
        if not self.analysis.domain_entities:
            return "## 🔄 Data Flow\n\nNo domain entities detected."
        
        content = f"## 🔄 Data Flow\n\nIdentified {len(self.analysis.domain_entities)} domain entities:\n\n"
        
        for entity in self.analysis.domain_entities:
            content += f"### {entity.name}\n"
            content += f"- **Type:** {entity.type}\n"
            content += f"- **File:** {entity.file_path.relative_to(self.analysis.root_path)}\n"
            
            if entity.fields:
                fields_str = ", ".join(entity.fields[:5])
                if len(entity.fields) > 5:
                    fields_str += f" ... (+{len(entity.fields) - 5} more)"
                content += f"- **Fields:** {fields_str}\n"
            
            if entity.methods:
                methods_str = ", ".join(entity.methods[:3])
                if len(entity.methods) > 3:
                    methods_str += f" ... (+{len(entity.methods) - 3} more)"
                content += f"- **Methods:** {methods_str}\n"
            
            content += "\n"
        
        return content
    
    def _generate_risks(self) -> str:
        """Generate risks and technical debt section."""
        risks = []
        
        if self.analysis.complexity_score > 70:
            risks.append("High complexity score indicates potential maintainability issues")
        
        if len(self.analysis.entry_points) == 0:
            risks.append("No clear entry points detected - may indicate unclear application structure")
        
        if len(self.analysis.execution_flows) < 2:
            risks.append("Limited execution flows detected - may indicate incomplete analysis or simple codebase")
        
        content = "## ⚠️ Known Issues\n\n"
        
        if risks:
            for risk in risks:
                content += f"- {risk}\n"
        else:
            content += "No significant risks detected in the current analysis.\n"
        
        return content + "\n"
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations section."""
        recommendations = []
        
        if self.analysis.complexity_score > 50:
            recommendations.append("Consider refactoring complex functions to improve maintainability")
        
        if len(self.analysis.domain_entities) > 0:
            recommendations.append("Document domain entities and their relationships for better understanding")
        
        if len(self.analysis.execution_flows) > 0:
            recommendations.append("Create sequence diagrams for critical execution flows")
        
        recommendations.append("Add comprehensive unit tests for core business logic")
        recommendations.append("Consider implementing code documentation standards")
        
        content = "## 💡 Recommendations\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"
        
        return content