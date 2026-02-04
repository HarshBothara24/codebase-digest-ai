"""Execution flow analysis."""

import networkx as nx
from typing import List, Set, Dict
from pathlib import Path

from ..models import CodebaseAnalysis, ExecutionFlow, CallRelation


class FlowAnalyzer:
    """Analyzes execution flows through the codebase."""
    
    def __init__(self, analysis: CodebaseAnalysis):
        self.analysis = analysis
        self.call_graph = self._build_call_graph()
    
    def _build_call_graph(self) -> nx.DiGraph:
        """Build a directed graph of function calls."""
        graph = nx.DiGraph()
        
        for call in self.analysis.call_relations:
            caller_name = call.caller_symbol.name
            graph.add_edge(caller_name, call.callee_name, 
                          caller_file=call.caller_symbol.file_path,
                          callee_file=call.callee_file,
                          line_number=call.line_number)
        
        return graph
    
    def analyze_flows(self) -> List[ExecutionFlow]:
        """Analyze execution flows starting from entry points."""
        flows = []
        
        # Find entry point functions
        entry_functions = self._find_entry_functions()
        
        for entry_func in entry_functions:
            flow = self._trace_execution_flow(entry_func)
            if flow:
                flows.append(flow)
        
        # Detect common patterns
        flows.extend(self._detect_common_patterns())
        
        return flows
    
    def _find_entry_functions(self) -> List[str]:
        """Find functions that are likely entry points."""
        entry_functions = []
        
        # Look for main functions
        for symbol in self.analysis.symbols:
            if symbol.name in ['main', '__main__', 'app', 'run', 'start']:
                entry_functions.append(symbol.name)
        
        # Look for HTTP route handlers
        for symbol in self.analysis.symbols:
            if any(decorator in ['@app.route', '@router.get', '@router.post', 
                               '@api.route', '@bp.route'] 
                   for decorator in symbol.decorators):
                entry_functions.append(symbol.name)
        
        return entry_functions
    
    def _trace_execution_flow(self, entry_function: str) -> ExecutionFlow:
        """Trace execution flow from an entry function."""
        if entry_function not in self.call_graph:
            return None
        
        # Use DFS to trace the flow
        visited = set()
        flow_steps = []
        files_involved = set()
        
        def dfs(func_name: str, depth: int = 0):
            if depth > 10 or func_name in visited:  # Prevent infinite recursion
                return
            
            visited.add(func_name)
            flow_steps.append(func_name)
            
            # Add file information
            for call in self.analysis.call_relations:
                if call.caller_symbol.name == func_name:
                    files_involved.add(call.caller_symbol.file_path)
                    if call.callee_file:
                        files_involved.add(call.callee_file)
            
            # Continue tracing
            if func_name in self.call_graph:
                for successor in self.call_graph.successors(func_name):
                    dfs(successor, depth + 1)
        
        dfs(entry_function)
        
        if len(flow_steps) > 1:
            return ExecutionFlow(
                name=f"{entry_function}_flow",
                entry_point=entry_function,
                steps=flow_steps,
                files_involved=files_involved,
                description=f"Execution flow starting from {entry_function}"
            )
        
        return None
    
    def _detect_common_patterns(self) -> List[ExecutionFlow]:
        """Detect common execution patterns."""
        patterns = []
        
        # Detect CRUD patterns
        crud_flow = self._detect_crud_pattern()
        if crud_flow:
            patterns.append(crud_flow)
        
        # Detect authentication patterns
        auth_flow = self._detect_auth_pattern()
        if auth_flow:
            patterns.append(auth_flow)
        
        return patterns
    
    def _detect_crud_pattern(self) -> ExecutionFlow:
        """Detect CRUD (Create, Read, Update, Delete) patterns."""
        crud_functions = []
        
        for symbol in self.analysis.symbols:
            name_lower = symbol.name.lower()
            if any(crud_word in name_lower for crud_word in 
                   ['create', 'read', 'get', 'update', 'delete', 'save', 'find']):
                crud_functions.append(symbol.name)
        
        if len(crud_functions) >= 3:  # At least 3 CRUD operations
            return ExecutionFlow(
                name="crud_operations",
                entry_point="CRUD Operations",
                steps=crud_functions,
                files_involved=set(),
                description="CRUD operations detected in the codebase"
            )
        
        return None
    
    def _detect_auth_pattern(self) -> ExecutionFlow:
        """Detect authentication/authorization patterns."""
        auth_functions = []
        
        for symbol in self.analysis.symbols:
            name_lower = symbol.name.lower()
            if any(auth_word in name_lower for auth_word in 
                   ['login', 'logout', 'authenticate', 'authorize', 'verify', 
                    'validate', 'token', 'session', 'permission']):
                auth_functions.append(symbol.name)
        
        if len(auth_functions) >= 2:
            return ExecutionFlow(
                name="authentication_flow",
                entry_point="Authentication System",
                steps=auth_functions,
                files_involved=set(),
                description="Authentication and authorization flow"
            )
        
        return None