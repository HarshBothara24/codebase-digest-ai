"""Interactive call graph exporter for developer inspection."""

from pathlib import Path
from typing import Dict, Any, List
import networkx as nx
from pyvis.network import Network

from ..models import CodebaseAnalysis, Symbol


class GraphExporter:
    """Exports call graph as interactive HTML visualization."""
    
    def __init__(self, analysis: CodebaseAnalysis, max_depth: int = None):
        self.analysis = analysis
        self.max_depth = max_depth
        self.graph = self._build_networkx_graph()
    
    def _build_networkx_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from analysis data."""
        G = nx.DiGraph()
        
        print(f"Building graph with {len(self.analysis.symbols)} symbols and {len(self.analysis.call_relations)} call relations")
        
        # Build symbol index for fast lookup
        symbol_index = {}
        for symbol in self.analysis.symbols:
            # Index by base name for resolution
            base_name = symbol.name.split('.')[-1]  # Handle Class.method -> method
            symbol_index.setdefault(base_name, []).append(symbol)
            # Also index by full name
            symbol_index.setdefault(symbol.name, []).append(symbol)
        
        # Add nodes for symbols
        for symbol in self.analysis.symbols:
            node_id = self._node_id(symbol)
            rel_path = symbol.file_path.relative_to(self.analysis.root_path)
            
            # Determine node color and size based on type
            color = self._get_node_color(symbol.type)
            size = self._get_node_size(symbol.type)
            
            G.add_node(
                node_id,
                label=symbol.name,
                title=f"{symbol.type}: {symbol.name}\nFile: {rel_path}\nLine: {symbol.line_number}",
                color=color,
                size=size,
                symbol_type=symbol.type,
                file_path=str(rel_path),
                line_number=symbol.line_number,
                docstring=symbol.docstring or "",
                group=str(symbol.file_path.name)  # Group by file for clustering
            )
        
        # Debug: Print some call relations
        print("Sample call relations:")
        for i, call in enumerate(self.analysis.call_relations[:5]):
            print(f"  {call.caller_symbol.name} -> {call.callee_name} (in {call.caller_symbol.file_path.name})")
        
        # Add edges for call relationships - now trivial with symbol-aware relations
        edges_added = 0
        unresolved_calls = []
        
        for call in self.analysis.call_relations:
            # Caller is now directly available as a symbol
            caller_id = self._node_id(call.caller_symbol)
            callee_id = None
            
            # Normalize callee name - strip object prefixes
            callee_base = call.callee_name.split(".")[-1]  # app.run -> run, self.validate -> validate
            
            # Strategy 1: Direct match with normalized name
            if callee_base in symbol_index:
                # Find best match (prefer same file, then any file)
                candidates = symbol_index[callee_base]
                
                # Prefer same file as caller
                same_file_candidates = [s for s in candidates if s.file_path == call.caller_symbol.file_path]
                if same_file_candidates:
                    symbol = same_file_candidates[0]
                    callee_id = self._node_id(symbol)
                else:
                    # Use first available candidate
                    symbol = candidates[0]
                    callee_id = self._node_id(symbol)
            
            # Strategy 2: Constructor calls (Class() -> Class.__init__ or just Class)
            elif call.callee_name in symbol_index:
                candidates = symbol_index[call.callee_name]
                # Look for class first
                class_candidates = [s for s in candidates if s.type == 'class']
                if class_candidates:
                    symbol = class_candidates[0]
                    callee_id = self._node_id(symbol)
                else:
                    symbol = candidates[0]
                    callee_id = self._node_id(symbol)
            
            # Strategy 3: Method calls (handle Class.method patterns)
            elif "." in call.callee_name:
                parts = call.callee_name.split(".")
                if len(parts) == 2:
                    class_name, method_name = parts
                    # Look for the method in the class
                    method_key = f"{class_name}.{method_name}"
                    if method_key in symbol_index:
                        symbol = symbol_index[method_key][0]
                        callee_id = self._node_id(symbol)
            
            # Add edge if callee found
            if callee_id and G.has_node(caller_id) and G.has_node(callee_id):
                G.add_edge(
                    caller_id,
                    callee_id,
                    title=f"{call.caller_symbol.name} → {call.callee_name}",
                    color="#666666",
                    width=2
                )
                edges_added += 1
            else:
                unresolved_calls.append(call.callee_name)
        
        print(f"Added {edges_added} edges to graph")
        
        # Debug: Show unresolved calls
        if unresolved_calls:
            print("Unresolved calls (first 10):")
            for callee in list(set(unresolved_calls))[:10]:
                print(f"  - {callee}")
        
        # Apply graph enhancements
        # Remove builtin noise and isolated nodes FIRST
        G = self._remove_builtin_noise(G)
        isolated = list(nx.isolates(G))
        G.remove_nodes_from(isolated)
        print(f"Removed {len(isolated)} isolated nodes")
        
        # Keep only largest connected component
        components = list(nx.weakly_connected_components(G))
        if components:
            largest = max(components, key=len)
            G = G.subgraph(largest).copy()
            print(f"Kept largest component with {len(largest)} nodes")
        
        # THEN enhance visualization (entrypoint marking happens after noise removal)
        self._enhance_graph_visualization(G)
        
        # Apply depth filtering if specified
        if self.max_depth is not None:
            G = self._apply_depth_filter(G, self.max_depth)
        
        return G
    
    def _apply_depth_filter(self, G: nx.DiGraph, max_depth: int) -> nx.DiGraph:
        """Filter graph to show only nodes within max_depth from detected entrypoints."""
        # Find detected entrypoints (nodes marked as entrypoints)
        entrypoints = [node for node in G.nodes() if G.nodes[node].get("entrypoint", False)]
        
        if not entrypoints:
            # Fallback: use probabilistic detection if no entrypoints marked yet
            entrypoints = self._detect_entrypoints(G)
        
        if not entrypoints:
            # Final fallback: return full graph if no entrypoints found
            print("No entrypoints detected for depth filtering - returning full graph")
            return G
        
        # Collect all nodes within max_depth from any entrypoint using BFS
        nodes_to_keep = set()
        for entry in entrypoints:
            if not G.has_node(entry):
                continue
                
            # BFS to find nodes within max_depth
            visited = {entry}
            queue = [(entry, 0)]
            
            while queue:
                node, depth = queue.pop(0)
                nodes_to_keep.add(node)
                
                if depth < max_depth:
                    for successor in G.successors(node):
                        if successor not in visited:
                            visited.add(successor)
                            queue.append((successor, depth + 1))
        
        # Create subgraph with only the nodes to keep
        filtered_graph = G.subgraph(nodes_to_keep).copy()
        print(f"Depth filter: reduced from {len(G.nodes())} to {len(filtered_graph.nodes())} nodes (depth={max_depth})")
        
        return filtered_graph
    
    def _detect_entrypoints(self, G: nx.DiGraph) -> List[str]:
        """Detect real execution entrypoints using weighted heuristic scoring."""
        entrypoint_candidates = []
        
        for node in G.nodes():
            # Parse node identifier
            parts = node.split("::")
            if len(parts) != 2:
                continue
                
            file_name = parts[0].lower()
            symbol_name = parts[1].lower()
            
            # Calculate weighted score
            score = 0
            
            # File-based signals
            if file_name in ("main.py", "app.py", "__main__.py"):
                score += 3
            elif file_name in ("cli.py", "server.py", "run.py"):
                score += 2
                
            # Symbol-based signals  
            if symbol_name in ("main", "run", "start"):
                score += 2
            elif symbol_name in ("app", "cli", "server"):
                score += 1
                
            # CLI bias: prefer "build" if present
            if symbol_name == "build":
                score += 3
                
            # Topology signals
            if G.in_degree(node) == 0:
                score += 1
                
            # Only consider nodes with meaningful score
            if score >= 3:
                entrypoint_candidates.append((node, score))
        
        # Sort by score descending
        entrypoint_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Keep only strongest entrypoint unless multiple are truly equal
        if entrypoint_candidates:
            top_score = entrypoint_candidates[0][1]
            dominant = [n for n, s in entrypoint_candidates if s == top_score]
            
            # Limit to max 2 for safety
            return dominant[:2]
        
        return []
    
    def _remove_builtin_noise(self, G: nx.DiGraph) -> nx.DiGraph:
        """Remove nodes that do not correspond to project symbols."""
        
        valid_nodes = set(self._node_id(s) for s in self.analysis.symbols)
        
        nodes_to_remove = [n for n in G.nodes() if n not in valid_nodes]
        
        G.remove_nodes_from(nodes_to_remove)
        print(f"Removed {len(nodes_to_remove)} non-project nodes")
        
        return G
    def _enhance_graph_visualization(self, G: nx.DiGraph) -> None:
        """Apply visual enhancements to make the graph more informative."""
        
        # 1. PROBABILISTIC ENTRYPOINT DETECTION
        entrypoints = self._detect_entrypoints(G)
        
        for node in entrypoints:
            if G.has_node(node):  # Ensure node still exists after noise removal
                G.nodes[node]["color"] = "#f59e0b"  # Orange for entrypoints
                G.nodes[node]["size"] += 12
                G.nodes[node]["entrypoint"] = True
        
        print(f"Detected {len(entrypoints)} probabilistic entrypoints: {[node.split('::')[-1] for node in entrypoints[:5]]}")
        
        # 2. CENTRALITY WEIGHTING - Size nodes by structural importance
        if len(G.nodes()) > 0:
            centrality = nx.degree_centrality(G)
            for node in G.nodes():
                importance_boost = int(centrality[node] * 20)
                G.nodes[node]["size"] += importance_boost
                
        # 3. EXECUTION PATH EMPHASIS - Mark immediate successors of entrypoints
        for entry in entrypoints:
            if G.has_node(entry):
                for successor in G.successors(entry):
                    if G.nodes[successor].get("color") != "#f59e0b":  # Don't override entrypoints
                        G.nodes[successor]["borderWidth"] = 3
                        G.nodes[successor]["borderColor"] = "#f59e0b"
    
    def _node_id(self, symbol: Symbol) -> str:
        """Generate consistent node ID for a symbol."""
        return f"{symbol.file_path.name}::{symbol.name}"
    
    def _get_node_color(self, symbol_type: str) -> str:
        """Get node color based on symbol type."""
        colors = {
            'function': '#3b82f6',  # blue
            'method': '#3b82f6',    # blue
            'class': '#10b981',     # green
            'file': '#6b7280'       # gray
        }
        return colors.get(symbol_type, '#6b7280')
    
    def _get_node_size(self, symbol_type: str) -> int:
        """Get node size based on symbol type."""
        sizes = {
            'class': 25,
            'function': 20,
            'method': 15,
            'file': 30
        }
        return sizes.get(symbol_type, 20)
    
    def export(self, output_path: Path) -> None:
        """Export graph as interactive HTML file."""
        # Add nodes and edges from NetworkX graph
        node_count = 0
        edge_count = 0
        
        # Collect nodes and edges data
        nodes_data = []
        edges_data = []
        
        for node_id, data in self.graph.nodes(data=True):
            nodes_data.append({
                'id': node_id,
                'label': data['label'],
                'title': data['title'],
                'color': data['color'],
                'size': data['size'],
                'group': data.get('group', 'default'),
                'font': {'color': '#1f2937'},
                'shape': 'dot'
            })
            node_count += 1
        
        for source, target, data in self.graph.edges(data=True):
            if self.graph.has_node(source) and self.graph.has_node(target):
                edges_data.append({
                    'from': source,
                    'to': target,
                    'title': data['title'],
                    'color': data['color'],
                    'width': data['width'],
                    'arrows': 'to'
                })
                edge_count += 1
        
        # Calculate real component count (handle empty graph)
        components = nx.number_weakly_connected_components(self.graph) if len(self.graph.nodes) > 0 else 0
        
        # If no edges, create a simple layout with isolated nodes
        if edge_count == 0:
            print(f"Warning: No edges found in graph. Showing {node_count} isolated nodes.")
        
        # Generate custom HTML with proper developer tool styling
        html_content = self._generate_developer_html(nodes_data, edges_data, node_count, edge_count, components)
        
        try:
            output_path.write_text(html_content, encoding='utf-8')
            print(f"Graph saved with {node_count} nodes and {edge_count} edges")
        except Exception as e:
            print(f"Error saving graph: {e}")
            # Fallback: create a simple HTML file
            self._create_fallback_html(output_path, node_count, edge_count)
    
    def _generate_developer_html(self, nodes_data: list, edges_data: list, node_count: int, edge_count: int, components: int) -> str:
        """Generate professional developer tool HTML with split layout."""
        import json
        
        nodes_json = json.dumps(nodes_data, indent=2)
        edges_json = json.dumps(edges_data, indent=2)
        
        warning_html = '''
        <div class="warning-banner">
            <div class="warning-icon">⚠️</div>
            <div>
                <strong>No connections found</strong>
                <p>Showing isolated nodes. This may indicate parsing issues or a codebase with minimal cross-references.</p>
            </div>
        </div>''' if edge_count == 0 else ''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Call Graph - {self.analysis.root_path.name}</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        :root {{
            --accent: #3b82f6;
            --bg: #f8fafc;
            --surface: #ffffff;
            --soft: #f1f5f9;
            --text: #0f172a;
            --muted: #64748b;
            --border: #e2e8f0;
            --danger: #ef4444;
            --warning: #f59e0b;
            --success: #10b981;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            height: 100vh;
            overflow: hidden;
        }}
        
        .app-shell {{
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        
        .header {{
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            padding: 16px 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .header h1 {{
            font-size: 18px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 4px;
        }}
        
        .header-meta {{
            font-size: 13px;
            color: var(--muted);
            display: flex;
            gap: 16px;
            align-items: center;
        }}
        
        .header-meta .accent {{
            color: var(--accent);
            font-weight: 500;
        }}
        
        .main-content {{
            flex: 1;
            display: flex;
            overflow: hidden;
        }}
        
        .graph-panel {{
            flex: 1;
            background: var(--surface);
            position: relative;
            border-right: 1px solid var(--border);
        }}
        
        .inspector-panel {{
            width: 320px;
            background: var(--surface);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        
        .inspector-header {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            background: var(--soft);
        }}
        
        .inspector-header h2 {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 4px;
        }}
        
        .inspector-header p {{
            font-size: 12px;
            color: var(--muted);
        }}
        
        .inspector-content {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }}
        
        .legend {{
            margin-bottom: 24px;
        }}
        
        .legend h3 {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 12px;
        }}
        
        .legend-items {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: var(--muted);
        }}
        
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid var(--border);
            flex-shrink: 0;
        }}
        
        .legend-functions {{ background: var(--accent); }}
        .legend-classes {{ background: var(--success); }}
        .legend-files {{ background: var(--muted); }}
        
        .stats-section {{
            margin-bottom: 24px;
        }}
        
        .stats-section h3 {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 12px;
        }}
        
        .stat-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            font-size: 12px;
            border-bottom: 1px solid var(--border);
        }}
        
        .stat-item:last-child {{
            border-bottom: none;
        }}
        
        .stat-label {{
            color: var(--muted);
        }}
        
        .stat-value {{
            color: var(--text);
            font-weight: 500;
        }}
        
        .node-info {{
            background: var(--soft);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
            display: none;
        }}
        
        .node-info.active {{
            display: block;
        }}
        
        .node-info h4 {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 8px;
        }}
        
        .node-info p {{
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 4px;
        }}
        
        .node-info .node-type {{
            display: inline-block;
            background: var(--accent);
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 500;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        
        .warning-banner {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 6px;
            padding: 12px;
            margin: 16px 20px;
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }}
        
        .warning-icon {{
            font-size: 16px;
            flex-shrink: 0;
        }}
        
        .warning-banner strong {{
            color: #92400e;
            font-size: 13px;
            display: block;
            margin-bottom: 4px;
        }}
        
        .warning-banner p {{
            color: #92400e;
            font-size: 12px;
            line-height: 1.4;
        }}
        
        #network {{
            width: 100%;
            height: 100%;
            background: var(--surface);
        }}
        
        .controls {{
            position: absolute;
            top: 16px;
            left: 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 8px 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 10;
        }}
        
        .controls button {{
            background: none;
            border: none;
            color: var(--muted);
            font-size: 12px;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            transition: all 0.15s ease;
        }}
        
        .controls button:hover {{
            background: var(--soft);
            color: var(--text);
        }}
        
        .empty-state {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 200px;
            color: var(--muted);
            font-size: 13px;
            text-align: center;
        }}
        
        .empty-state-icon {{
            font-size: 24px;
            margin-bottom: 8px;
            opacity: 0.5;
        }}
        
        .insights-section {{
            margin-bottom: 24px;
        }}
        
        .insights-section h3 {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 12px;
        }}
        
        .insight-item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 12px;
            padding: 8px;
            background: var(--soft);
            border-radius: 4px;
        }}
        
        .insight-icon {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            flex-shrink: 0;
        }}
        
        .insight-item strong {{
            font-size: 12px;
            color: var(--text);
            display: block;
            margin-bottom: 2px;
        }}
        
        .insight-item p {{
            font-size: 11px;
            color: var(--muted);
            line-height: 1.3;
        }}
    </style>
</head>
<body>
    <div class="app-shell">
        <div class="header">
            <h1>Call Graph: {self.analysis.root_path.name}</h1>
            <div class="header-meta">
                <span>Interactive visualization of function and method call relationships</span>
                <span class="accent">{node_count} nodes</span>
                <span class="accent">{edge_count} edges</span>
            </div>
        </div>
        
        {warning_html}
        
        <div class="main-content">
            <div class="graph-panel">
                <div class="controls">
                    <button onclick="network.fit()">Fit View</button>
                    <button onclick="togglePhysics()">Toggle Physics</button>
                </div>
                <div id="network"></div>
            </div>
            
            <div class="inspector-panel">
                <div class="inspector-header">
                    <h2>Graph Inspector</h2>
                    <p>Click nodes to inspect details</p>
                </div>
                
                <div class="inspector-content">
                    <div class="legend">
                        <h3>Legend</h3>
                        <div class="legend-items">
                            <div class="legend-item">
                                <div class="legend-dot legend-functions"></div>
                                <span>Functions & Methods</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-dot legend-classes"></div>
                                <span>Classes</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-dot legend-files"></div>
                                <span>Files</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="stats-section">
                        <h3>Statistics</h3>
                        <div class="stat-item">
                            <span class="stat-label">Total Nodes</span>
                            <span class="stat-value">{node_count}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Total Edges</span>
                            <span class="stat-value">{edge_count}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Files Analyzed</span>
                            <span class="stat-value">{len(set(node['group'] for node in nodes_data))}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Entrypoints</span>
                            <span class="stat-value" id="entrypoint-count">-</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Components</span>
                            <span class="stat-value">{components}</span>
                        </div>
                    </div>
                    
                    <div class="insights-section">
                        <h3>Graph Insights</h3>
                        <div class="insight-item">
                            <div class="insight-icon" style="background: #f59e0b;">🚀</div>
                            <div>
                                <strong>Entrypoints</strong>
                                <p>Orange nodes show execution starting points</p>
                            </div>
                        </div>
                        <div class="insight-item">
                            <div class="insight-icon" style="background: #3b82f6;">🔗</div>
                            <div>
                                <strong>Call Chains</strong>
                                <p>Follow arrows to trace execution flow</p>
                            </div>
                        </div>
                        <div class="insight-item">
                            <div class="insight-icon" style="background: #10b981;">📦</div>
                            <div>
                                <strong>Clusters</strong>
                                <p>Related functions group naturally</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="node-info" id="nodeInfo">
                        <div class="empty-state">
                            <div class="empty-state-icon">👆</div>
                            <p>Click a node to view details</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script type="text/javascript">
        // Initialize data
        const nodes = new vis.DataSet({nodes_json});
        const edges = new vis.DataSet({edges_json});
        
        // Network options with improved physics
        const options = {{
            physics: {{
                enabled: true,
                stabilization: {{ iterations: 300 }},
                barnesHut: {{
                    gravitationalConstant: -6000,
                    centralGravity: 0.3,
                    springLength: 120,
                    springConstant: 0.08,
                    damping: 0.1,
                    avoidOverlap: 0.2
                }}
            }},
            nodes: {{
                font: {{
                    size: 14,
                    face: "system-ui, -apple-system, sans-serif"
                }},
                borderWidth: 2,
                shadow: {{
                    enabled: true,
                    color: "rgba(0,0,0,0.2)",
                    size: 5,
                    x: 2,
                    y: 2
                }},
                chosen: true
            }},
            edges: {{
                arrows: {{
                    to: {{ enabled: true, scaleFactor: 0.8 }}
                }},
                smooth: {{ type: "continuous" }},
                color: {{ color: "#666666", highlight: "#3b82f6" }},
                width: 2
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: false,
                hideNodesOnDrag: false
            }},
            layout: {{
                improvedLayout: true,
                randomSeed: 42
            }},
            groups: {{
                useDefaultGroups: true
            }}
        }};
        
        // Initialize network
        const container = document.getElementById('network');
        const data = {{ nodes: nodes, edges: edges }};
        const network = new vis.Network(container, data, options);
        
        // Node click handler
        network.on("click", function(params) {{
            const nodeInfo = document.getElementById('nodeInfo');
            
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                
                // Extract info from title
                const titleParts = node.title.split('\\n');
                const type = titleParts[0].split(': ')[0];
                const name = titleParts[0].split(': ')[1];
                const file = titleParts[1] ? titleParts[1].split(': ')[1] : 'Unknown';
                const line = titleParts[2] ? titleParts[2].split(': ')[1] : 'Unknown';
                
                nodeInfo.innerHTML = `
                    <div class="node-type">${{type}}</div>
                    <h4>${{name}}</h4>
                    <p><strong>File:</strong> ${{file}}</p>
                    <p><strong>Line:</strong> ${{line}}</p>
                    <p><strong>Group:</strong> ${{node.group}}</p>
                `;
                nodeInfo.classList.add('active');
            }} else {{
                nodeInfo.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">👆</div>
                        <p>Click a node to view details</p>
                    </div>
                `;
                nodeInfo.classList.remove('active');
            }}
        }});
        
        // Physics toggle
        let physicsEnabled = true;
        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            network.setOptions({{ physics: {{ enabled: physicsEnabled }} }});
        }}
        
        // Cluster by file groups if we have many nodes
        if (nodes.length > 20) {{
            
        }}
        
        // Auto-fit on load
        network.once("stabilizationIterationsDone", function() {{
            network.fit();
            
            // Update dynamic statistics
            updateGraphStats();
        }});
        
        function updateGraphStats() {{
            // Count entrypoints (orange nodes)
            const entrypoints = nodes.get({{
                filter: function(node) {{
                    return node.color === '#f59e0b';
                }}
            }});
            document.getElementById('entrypoint-count').textContent = entrypoints.length;
        }}
    </script>
</body>
</html>'''
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the call graph."""
        # Handle empty graph case
        if len(self.graph.nodes) == 0:
            return {
                'nodes': 0,
                'edges': 0,
                'density': 0.0,
                'is_connected': False,
                'components': 0
            }
        
        return {
            'nodes': len(self.graph.nodes),
            'edges': len(self.graph.edges),
            'density': nx.density(self.graph) if len(self.graph.edges) > 0 else 0.0,
            'is_connected': nx.is_weakly_connected(self.graph) if len(self.graph.nodes) > 0 else False,
            'components': nx.number_weakly_connected_components(self.graph) if len(self.graph.nodes) > 0 else 0
        }
    
    def _create_fallback_html(self, output_path: Path, node_count: int, edge_count: int) -> None:
        """Create a simple fallback HTML when pyvis fails."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Call Graph - {self.analysis.root_path.name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #f8fafc;
            color: #1f2937;
            padding: 24px;
        }}
        .header {{
            background: white;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            margin-bottom: 24px;
        }}
        .stats {{
            background: #f3f4f6;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 24px;
        }}
        .node-list {{
            background: white;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }}
        .node-item {{
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .node-item:last-child {{
            border-bottom: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Call Graph: {self.analysis.root_path.name}</h1>
        <p>Graph visualization failed. Showing node list instead.</p>
    </div>
    
    <div class="stats">
        <p>Nodes: {node_count} | Edges: {edge_count}</p>
    </div>
    
    <div class="node-list">
        <h2>Detected Symbols</h2>
        {''.join(f'<div class="node-item">{symbol.name} ({symbol.type}) - {symbol.file_path.name}:{symbol.line_number}</div>' for symbol in self.analysis.symbols[:20])}
        {f'<div class="node-item">... and {len(self.analysis.symbols) - 20} more</div>' if len(self.analysis.symbols) > 20 else ''}
    </div>
</body>
</html>"""
        output_path.write_text(html_content, encoding='utf-8')