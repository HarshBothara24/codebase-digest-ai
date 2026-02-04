"""HTML report exporter."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from ..models import CodebaseAnalysis


class HTMLExporter:
    """Exports analysis results to HTML format."""
    
    def __init__(self, analysis: CodebaseAnalysis):
        self.analysis = analysis
    
    def export(self, output_path: Path) -> None:
        """Export analysis to HTML file."""
        html_content = self._generate_html()
        output_path.write_text(html_content, encoding='utf-8')
    
    def _generate_html(self) -> str:
        """Generate complete HTML report."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Codebase Analysis - {self.analysis.root_path.name}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_project_summary()}
        {self._generate_summary_metrics()}
        {self._generate_architecture()}
        {self._generate_directory_structure()}
        {self._generate_key_components()}
        {self._generate_core_logic()}
        {self._generate_dependencies()}
        {self._generate_data_flow()}
        {self._generate_risks()}
        {self._generate_recommendations()}
    </div>
</body>
</html>"""
    
    def _get_css(self) -> str:
        """Generate CSS styles."""
        return """
        :root {
            --accent: #3b82f6;
            --bg: #f8fafc;
            --surface: #ffffff;
            --soft: #f1f5f9;
            --text: #0f172a;
            --muted: #64748b;
            --border: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --radius: 8px;
            --spacing-xs: 8px;
            --spacing-sm: 12px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            --spacing-2xl: 48px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: var(--text);
            background: var(--bg);
            -webkit-font-smoothing: antialiased;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: var(--spacing-lg);
            padding-top: 120px;
        }
        
        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid var(--border);
            z-index: 100;
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: var(--spacing-lg);
        }
        
        .header h1 {
            font-size: 32px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: var(--spacing-sm);
            letter-spacing: -0.025em;
        }
        
        .meta-row {
            display: flex;
            gap: var(--spacing-xl);
            font-size: 12px;
            color: var(--muted);
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
        }
        
        .meta-label {
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .project-summary {
            background: linear-gradient(135deg, var(--surface) 0%, var(--soft) 100%);
            padding: var(--spacing-2xl);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent);
            margin-bottom: var(--spacing-2xl);
            box-shadow: var(--shadow-sm);
        }
        
        .project-summary h2 {
            font-size: 18px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: var(--spacing-md);
            letter-spacing: -0.01em;
        }
        
        .project-summary p {
            color: var(--muted);
            line-height: 1.6;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: var(--spacing-lg);
            margin-bottom: var(--spacing-2xl);
        }
        
        .metric-card {
            background: var(--surface);
            padding: var(--spacing-xl);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            border-top: 3px solid var(--accent);
            box-shadow: var(--shadow-sm);
            transition: all 150ms ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        .metric-value {
            font-size: 36px;
            font-weight: 800;
            color: var(--text);
            margin-bottom: var(--spacing-xs);
            line-height: 1;
            letter-spacing: -0.02em;
        }
        
        .metric-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 4px;
        }
        
        .metric-caption {
            font-size: 12px;
            color: var(--muted);
            line-height: 1.4;
        }
        
        .section {
            background: var(--surface);
            padding: var(--spacing-2xl);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent);
            margin-bottom: var(--spacing-xl);
            box-shadow: var(--shadow-sm);
            transition: box-shadow 150ms ease;
        }
        
        .section:nth-child(even) {
            background: var(--soft);
        }
        
        .section:hover {
            box-shadow: var(--shadow-md);
        }
        
        .section h2 {
            font-size: 18px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: var(--spacing-xl);
            padding-bottom: var(--spacing-md);
            border-bottom: 1px solid var(--border);
            letter-spacing: -0.01em;
        }
        
        .section h3 {
            font-size: 14px;
            font-weight: 700;
            color: var(--text);
            margin: var(--spacing-xl) 0 var(--spacing-md) 0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .directory-tree {
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
            font-size: 13px;
            background: #1e293b;
            color: #e2e8f0;
            padding: var(--spacing-lg);
            border-radius: var(--radius);
            line-height: 1.6;
            white-space: pre;
            overflow-x: auto;
        }
        
        .component-tables {
            display: grid;
            gap: var(--spacing-2xl);
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            border-radius: var(--radius);
            overflow: hidden;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
        }
        
        .table th,
        .table td {
            padding: var(--spacing-md) var(--spacing-lg);
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        .table th {
            background: var(--soft);
            font-weight: 700;
            color: var(--text);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .table td {
            color: var(--muted);
            font-size: 14px;
        }
        
        .table tbody tr {
            transition: background-color 150ms ease;
        }
        
        .table tbody tr:hover {
            background: var(--soft);
        }
        
        .table tbody tr:last-child td {
            border-bottom: none;
        }
        
        .flow-timeline {
            position: relative;
            padding-left: var(--spacing-xl);
        }
        
        .flow-timeline::before {
            content: '';
            position: absolute;
            left: 12px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--accent);
        }
        
        .flow-card {
            position: relative;
            background: var(--surface);
            padding: var(--spacing-lg);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--shadow-sm);
            margin-left: var(--spacing-lg);
            transition: all 150ms ease;
        }
        
        .flow-card::before {
            content: '';
            position: absolute;
            left: -31px;
            top: 20px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--accent);
            border: 3px solid var(--surface);
        }
        
        .flow-card:hover {
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }
        
        .flow-card:last-child {
            margin-bottom: 0;
        }
        
        .flow-name {
            font-size: 16px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: var(--spacing-xs);
        }
        
        .flow-description {
            font-size: 14px;
            color: var(--muted);
            margin-bottom: var(--spacing-md);
            line-height: 1.5;
        }
        
        .flow-steps {
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
            font-size: 12px;
            color: var(--text);
            background: var(--soft);
            padding: var(--spacing-md);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            line-height: 1.4;
        }
        
        .dependency-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--spacing-md) 0;
            border-bottom: 1px solid var(--border);
            transition: all 150ms ease;
        }
        
        .dependency-item:hover {
            background: var(--soft);
            margin: 0 calc(-1 * var(--spacing-xl));
            padding-left: var(--spacing-xl);
            padding-right: var(--spacing-xl);
            border-radius: var(--radius);
        }
        
        .dependency-item:last-child {
            border-bottom: none;
        }
        
        .dependency-name {
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
            font-size: 14px;
            color: var(--text);
            font-weight: 600;
        }
        
        .dependency-bar {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            min-width: 140px;
        }
        
        .dependency-count {
            font-size: 12px;
            color: var(--muted);
            min-width: 24px;
            font-weight: 600;
        }
        
        .dependency-rail {
            flex: 1;
            height: 6px;
            background: var(--soft);
            border-radius: 3px;
            overflow: hidden;
            border: 1px solid var(--border);
        }
        
        .bar {
            height: 100%;
            background: var(--accent);
            border-radius: 2px;
            min-width: 2px;
            transition: width 300ms ease;
        }
        
        .risk-item {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-md);
            box-shadow: var(--shadow-sm);
            transition: all 150ms ease;
        }
        
        .risk-item:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }
        
        .risk-item.low {
            border-left: 4px solid var(--accent);
        }
        
        .risk-item.medium {
            border-left: 4px solid #f59e0b;
        }
        
        .risk-item.high {
            border-left: 4px solid #ef4444;
        }
        
        .risk-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-sm);
        }
        
        .risk-severity {
            font-size: 10px;
            font-weight: 800;
            padding: 4px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .risk-severity.low {
            background: var(--accent);
            color: white;
        }
        
        .risk-severity.medium {
            background: #f59e0b;
            color: white;
        }
        
        .risk-severity.high {
            background: #ef4444;
            color: white;
        }
        
        .risk-reason {
            font-size: 14px;
            font-weight: 700;
            color: var(--text);
        }
        
        .risk-evidence {
            font-size: 12px;
            color: var(--muted);
            margin-top: 4px;
            line-height: 1.4;
        }
        
        .recommendation-item {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-md);
            box-shadow: var(--shadow-sm);
            transition: all 150ms ease;
            border-left: 4px solid var(--accent);
        }
        
        .recommendation-item:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }
        
        .recommendation-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-sm);
        }
        
        .recommendation-priority {
            font-size: 10px;
            font-weight: 800;
            padding: 4px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .recommendation-priority.high {
            background: #ef4444;
            color: white;
        }
        
        .recommendation-priority.medium {
            background: #f59e0b;
            color: white;
        }
        
        .recommendation-priority.low {
            background: var(--accent);
            color: white;
        }
        
        .recommendation-text {
            font-size: 14px;
            font-weight: 700;
            color: var(--text);
        }
        
        .recommendation-rationale {
            font-size: 12px;
            color: var(--muted);
            margin-top: 4px;
            line-height: 1.4;
        }
        
        .recommendation-actions {
            margin-top: var(--spacing-md);
        }
        
        .recommendation-link {
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-xs);
            color: var(--accent);
            text-decoration: none;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: 4px;
            transition: all 150ms ease;
        }
        
        .recommendation-link:hover {
            background: var(--soft);
            color: var(--text);
            transform: translateX(2px);
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            background: var(--soft);
            color: var(--muted);
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid var(--border);
        }
        """
    
    def _generate_header(self) -> str:
        """Generate header section."""
        primary_language = list(self.analysis.languages)[0] if self.analysis.languages else 'Unknown'
        
        return f"""
        <div class="header">
            <div class="header-content">
                <h1>{self.analysis.root_path.name}</h1>
                <div class="meta-row">
                    <div class="meta-item">
                        <span class="meta-label">Primary Language:</span>
                        <span>{primary_language}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Total LOC:</span>
                        <span>{self.analysis.total_lines:,}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Generated:</span>
                        <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_project_summary(self) -> str:
        """Generate project summary section."""
        # Infer project type and domain from analysis
        domain_entities = [entity.name.lower() for entity in self.analysis.domain_entities]
        
        # Determine domain
        domain = "Unknown"
        if any(term in domain_entities for term in ['user', 'account', 'auth']):
            if any(term in domain_entities for term in ['payment', 'wallet', 'transaction']):
                domain = "Financial/Payment System"
            else:
                domain = "User Management System"
        elif any(term in domain_entities for term in ['payment', 'wallet', 'transaction']):
            domain = "Financial Application"
        elif any(term in domain_entities for term in ['product', 'inventory', 'catalog']):
            domain = "E-commerce/Inventory System"
        elif len(domain_entities) > 0:
            domain = "Business Application"
        
        # Determine architectural style
        arch_style = "Modular"
        if len(self.analysis.execution_flows) > 2:
            arch_style = "Service-oriented"
        if any('service' in symbol.name.lower() for symbol in self.analysis.symbols):
            arch_style = "Service Layer Architecture"
        
        # Generate description
        entity_count = len(self.analysis.domain_entities)
        service_count = len([s for s in self.analysis.symbols if 'service' in s.name.lower() and s.type == 'class'])
        
        description = f"This project appears to be a {domain.lower()} implementing a {arch_style.lower()}."
        if entity_count > 0:
            description += f" The system defines {entity_count} core domain entities"
            if service_count > 0:
                description += f" with {service_count} service classes handling business logic"
            description += "."
        
        if len(self.analysis.execution_flows) > 0:
            description += f" Analysis identified {len(self.analysis.execution_flows)} distinct execution flows through the system."
        
        return f"""
        <div class="project-summary">
            <h2>Project Summary</h2>
            <p>{description}</p>
        </div>
        """
    
    def _generate_summary_metrics(self) -> str:
        """Generate summary metrics cards."""
        return f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{self.analysis.total_files}</div>
                <div class="metric-title">Total Files</div>
                <div class="metric-caption">Across {len(self.analysis.languages)} languages</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.analysis.total_lines:,}</div>
                <div class="metric-title">Lines of Code</div>
                <div class="metric-caption">Excluding comments and blanks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(self.analysis.symbols)}</div>
                <div class="metric-title">Code Symbols</div>
                <div class="metric-caption">Functions, classes, and methods</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.analysis.complexity_score:.1f}</div>
                <div class="metric-title">Complexity Score</div>
                <div class="metric-caption">Based on call relationships</div>
            </div>
        </div>
        """
    
    def _generate_architecture(self) -> str:
        """Generate architecture section."""
        return f"""
        <div class="section" id="architecture">
            <h2>Architecture</h2>
            <p>The codebase follows a modular architecture with {len(self.analysis.symbols)} defined symbols 
            and {len(self.analysis.call_relations)} call relationships.</p>
            
            <h3>Key Statistics</h3>
            <ul>
                <li>Functions: {len([s for s in self.analysis.symbols if s.type == 'function'])}</li>
                <li>Classes: {len([s for s in self.analysis.symbols if s.type == 'class'])}</li>
                <li>Methods: {len([s for s in self.analysis.symbols if s.type == 'method'])}</li>
                <li>Domain Entities: {len(self.analysis.domain_entities)}</li>
            </ul>
        </div>
        """
    
    def _generate_directory_structure(self) -> str:
        """Generate directory structure section."""
        tree_text = self._render_directory_tree_text(self.analysis.directory_tree, self.analysis.root_path.name)
        
        return f"""
        <div class="section">
            <h2>Directory Structure</h2>
            <div class="directory-tree">{tree_text}</div>
        </div>
        """
    
    def _render_directory_tree_text(self, tree: Dict, root_name: str, prefix: str = "") -> str:
        """Render directory tree as plain text."""
        if not tree:
            return f"{root_name}/\n"
        
        lines = [f"{root_name}/"]
        items = [(k, v) for k, v in tree.items() if k != '_files']
        files = tree.get('_files', [])
        
        # Add directories
        for i, (key, value) in enumerate(items):
            is_last_dir = i == len(items) - 1 and not files
            current_prefix = "└── " if is_last_dir else "├── "
            lines.append(f"{prefix}{current_prefix}{key}/")
            
            if isinstance(value, dict):
                next_prefix = prefix + ("    " if is_last_dir else "│   ")
                subtree = self._render_directory_tree_text(value, "", next_prefix)
                lines.extend(subtree.strip().split('\n')[1:])  # Skip the root line
        
        # Add files
        for i, file in enumerate(files):
            is_last = i == len(files) - 1
            file_prefix = "└── " if is_last else "├── "
            lines.append(f"{prefix}{file_prefix}{file}")
        
        return '\n'.join(lines)
    
    def _generate_key_components(self) -> str:
        """Generate key components section with separate tables."""
        classes = [s for s in self.analysis.symbols if s.type == 'class']
        functions = [s for s in self.analysis.symbols if s.type == 'function']
        methods = [s for s in self.analysis.symbols if s.type == 'method']
        
        return f"""
        <div class="section" id="key-components">
            <h2>Key Components</h2>
            <div class="component-tables">
                {self._generate_component_table("Classes", classes)}
                {self._generate_component_table("Functions", functions)}
                {self._generate_component_table("Methods", methods)}
            </div>
        </div>
        """
    
    def _generate_component_table(self, title: str, symbols: list) -> str:
        """Generate a component table for a specific symbol type."""
        if not symbols:
            return f"""
            <div>
                <h3>{title}</h3>
                <p>No {title.lower()} found.</p>
            </div>
            """
        
        # Limit to top 10 for readability
        symbols = symbols[:10]
        
        table_rows = ""
        for symbol in symbols:
            rel_path = symbol.file_path.relative_to(self.analysis.root_path)
            docstring = symbol.docstring[:50] + "..." if symbol.docstring and len(symbol.docstring) > 50 else (symbol.docstring or "")
            
            table_rows += f"""
            <tr>
                <td><code>{symbol.name}</code></td>
                <td>{rel_path}</td>
                <td>{symbol.line_number}</td>
                <td>{docstring}</td>
            </tr>
            """
        
        return f"""
        <div>
            <h3>{title}</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>File</th>
                        <th>Line</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_core_logic(self) -> str:
        """Generate core logic section with flow timeline."""
        if not self.analysis.execution_flows:
            return f"""
            <div class="section">
                <h2>Core Logic</h2>
                <p>No execution flows detected in the codebase.</p>
            </div>
            """
        
        flow_cards = ""
        for flow in self.analysis.execution_flows:
            steps_text = " → ".join(flow.steps[:5])
            if len(flow.steps) > 5:
                steps_text += f" → ... (+{len(flow.steps) - 5} more)"
            
            flow_cards += f"""
            <div class="flow-card">
                <div class="flow-name">{flow.name.replace('_', ' ').title()}</div>
                <div class="flow-description">{flow.description}</div>
                <div class="flow-steps">{steps_text}</div>
            </div>
            """
        
        return f"""
        <div class="section" id="core-logic">
            <h2>Core Logic</h2>
            <div class="flow-timeline">
                {flow_cards}
            </div>
        </div>
        """
    
    def _generate_dependencies(self) -> str:
        """Generate dependencies section with usage bars."""
        if not self.analysis.imports:
            return f"""
            <div class="section">
                <h2>Dependencies</h2>
                <p>No imports detected.</p>
            </div>
            """
        
        # Group imports by module
        import_counts = {}
        for imp in self.analysis.imports:
            if imp.module not in import_counts:
                import_counts[imp.module] = 0
            import_counts[imp.module] += 1
        
        # Sort by frequency
        top_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        max_count = max(count for _, count in top_imports) if top_imports else 1
        
        dependency_items = ""
        for module, count in top_imports:
            bar_width = (count / max_count) * 100
            dependency_items += f"""
            <div class="dependency-item">
                <div class="dependency-name">{module}</div>
                <div class="dependency-bar">
                    <div class="dependency-count">{count}</div>
                    <div class="dependency-rail">
                        <div class="bar" style="width: {bar_width}%;"></div>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>Dependencies</h2>
            <div>
                {dependency_items}
            </div>
        </div>
        """
    
    def _generate_data_flow(self) -> str:
        """Generate data flow section."""
        entities_html = ""
        for entity in self.analysis.domain_entities:
            fields_str = ", ".join(entity.fields[:5])
            if len(entity.fields) > 5:
                fields_str += f" ... (+{len(entity.fields) - 5} more)"
            
            entities_html += f"""
            <div class="info">
                <strong>{entity.name}</strong> ({entity.type})<br>
                Fields: {fields_str}<br>
                File: {entity.file_path.relative_to(self.analysis.root_path)}
            </div>
            """
        
        return f"""
        <div class="section" id="data-flow">
            <h2>Data Flow</h2>
            <p>Identified {len(self.analysis.domain_entities)} domain entities:</p>
            {entities_html}
        </div>
        """
    
    def _generate_risks(self) -> str:
        """Generate risks and technical debt section."""
        risks = []
        
        if self.analysis.complexity_score > 70:
            risks.append({
                'severity': 'high',
                'reason': 'High complexity score indicates potential maintainability issues',
                'evidence': f'Complexity score: {self.analysis.complexity_score:.1f}/100'
            })
        elif self.analysis.complexity_score > 40:
            risks.append({
                'severity': 'medium',
                'reason': 'Moderate complexity may impact long-term maintainability',
                'evidence': f'Complexity score: {self.analysis.complexity_score:.1f}/100'
            })
        
        if len(self.analysis.entry_points) == 0:
            risks.append({
                'severity': 'medium',
                'reason': 'No clear entry points detected',
                'evidence': 'May indicate unclear application structure or missing main files'
            })
        
        if len(self.analysis.execution_flows) < 2:
            risks.append({
                'severity': 'low',
                'reason': 'Limited execution flows detected',
                'evidence': f'Only {len(self.analysis.execution_flows)} flows identified - may indicate simple codebase or incomplete analysis'
            })
        
        # If no risks, add a low-severity default
        if not risks:
            risks.append({
                'severity': 'low',
                'reason': 'No significant risks detected',
                'evidence': 'Codebase appears well-structured based on current analysis'
            })
        
        risk_items = ""
        for risk in risks:
            risk_items += f"""
            <div class="risk-item {risk['severity']}">
                <div class="risk-header">
                    <span class="risk-severity {risk['severity']}">{risk['severity']}</span>
                    <span class="risk-reason">{risk['reason']}</span>
                </div>
                <div class="risk-evidence">{risk['evidence']}</div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>Risks / Technical Debt</h2>
            {risk_items}
        </div>
        """
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations section."""
        recommendations = []
        
        if self.analysis.complexity_score > 50:
            recommendations.append({
                'priority': 'high',
                'text': 'Consider refactoring complex functions to improve maintainability',
                'rationale': f'Current complexity score of {self.analysis.complexity_score:.1f} suggests potential maintainability challenges',
                'action': 'Review functions with high cyclomatic complexity',
                'link': '#key-components'
            })
        
        if len(self.analysis.domain_entities) > 0:
            recommendations.append({
                'priority': 'medium',
                'text': 'Document domain entities and their relationships',
                'rationale': f'Found {len(self.analysis.domain_entities)} domain entities that would benefit from clear documentation',
                'action': 'Create entity relationship diagrams',
                'link': '#data-flow'
            })
        
        if len(self.analysis.execution_flows) > 0:
            recommendations.append({
                'priority': 'medium',
                'text': 'Create sequence diagrams for critical execution flows',
                'rationale': f'Identified {len(self.analysis.execution_flows)} execution flows that could be visualized for better understanding',
                'action': 'Document flow sequences',
                'link': '#core-logic'
            })
        
        recommendations.append({
            'priority': 'low',
            'text': 'Add comprehensive unit tests for core business logic',
            'rationale': 'Testing coverage analysis not performed - recommended for production systems',
            'action': 'Set up testing framework and write tests',
            'link': '#key-components'
        })
        
        recommendations.append({
            'priority': 'low',
            'text': 'Consider implementing code documentation standards',
            'rationale': 'Consistent documentation improves maintainability and onboarding',
            'action': 'Establish documentation guidelines',
            'link': '#architecture'
        })
        
        rec_items = ""
        for rec in recommendations:
            rec_items += f"""
            <div class="recommendation-item">
                <div class="recommendation-header">
                    <span class="recommendation-priority {rec['priority']}">{rec['priority']}</span>
                    <span class="recommendation-text">{rec['text']}</span>
                </div>
                <div class="recommendation-rationale">{rec['rationale']}</div>
                <div class="recommendation-actions">
                    <a href="{rec['link']}" class="recommendation-link">
                        {rec['action']} →
                    </a>
                </div>
            </div>
            """
        
        return f"""
        <div class="section" id="recommendations">
            <h2>Recommendations</h2>
            {rec_items}
        </div>
        """