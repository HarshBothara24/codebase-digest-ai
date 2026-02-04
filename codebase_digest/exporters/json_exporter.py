"""JSON data exporter."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from ..models import CodebaseAnalysis, Symbol, Import, CallRelation, DomainEntity, ExecutionFlow


class JSONExporter:
    """Exports analysis results to JSON format."""
    
    def __init__(self, analysis: CodebaseAnalysis):
        self.analysis = analysis
    
    def export(self, output_path: Path) -> None:
        """Export analysis to JSON file."""
        json_data = self._generate_json()
        output_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
    
    def _generate_json(self) -> Dict[str, Any]:
        """Generate complete JSON data structure."""
        return {
            "metadata": {
                "project_name": self.analysis.root_path.name,
                "root_path": str(self.analysis.root_path),
                "generated_at": datetime.now().isoformat(),
                "version": "0.1.0"
            },
            "metrics": {
                "total_files": self.analysis.total_files,
                "total_lines": self.analysis.total_lines,
                "languages": list(self.analysis.languages),
                "complexity_score": self.analysis.complexity_score,
                "symbol_count": len(self.analysis.symbols),
                "import_count": len(self.analysis.imports),
                "call_relation_count": len(self.analysis.call_relations),
                "domain_entity_count": len(self.analysis.domain_entities),
                "execution_flow_count": len(self.analysis.execution_flows)
            },
            "entry_points": [str(ep) for ep in self.analysis.entry_points],
            "symbols": [self._serialize_symbol(symbol) for symbol in self.analysis.symbols],
            "imports": [self._serialize_import(imp) for imp in self.analysis.imports],
            "call_relations": [self._serialize_call_relation(call) for call in self.analysis.call_relations],
            "domain_entities": [self._serialize_domain_entity(entity) for entity in self.analysis.domain_entities],
            "execution_flows": [self._serialize_execution_flow(flow) for flow in self.analysis.execution_flows],
            "directory_tree": self.analysis.directory_tree
        }
    
    def _serialize_symbol(self, symbol: Symbol) -> Dict[str, Any]:
        """Serialize a Symbol to JSON-compatible dict."""
        return {
            "name": symbol.name,
            "type": symbol.type,
            "file_path": str(symbol.file_path),
            "line_number": symbol.line_number,
            "docstring": symbol.docstring,
            "parameters": symbol.parameters,
            "return_type": symbol.return_type,
            "decorators": symbol.decorators
        }
    
    def _serialize_import(self, imp: Import) -> Dict[str, Any]:
        """Serialize an Import to JSON-compatible dict."""
        return {
            "module": imp.module,
            "names": imp.names,
            "alias": imp.alias,
            "file_path": str(imp.file_path) if imp.file_path else None,
            "line_number": imp.line_number
        }
    
    def _serialize_call_relation(self, call: CallRelation) -> Dict[str, Any]:
        """Serialize a CallRelation to JSON-compatible dict."""
        return {
            "caller": call.caller_symbol.name,
            "callee": call.callee_name,
            "caller_file": str(call.caller_symbol.file_path),
            "callee_file": str(call.callee_file) if call.callee_file else None,
            "line_number": call.line_number
        }
    
    def _serialize_domain_entity(self, entity: DomainEntity) -> Dict[str, Any]:
        """Serialize a DomainEntity to JSON-compatible dict."""
        return {
            "name": entity.name,
            "type": entity.type,
            "file_path": str(entity.file_path),
            "fields": entity.fields,
            "methods": entity.methods,
            "creation_points": entity.creation_points,
            "modification_points": entity.modification_points,
            "validation_points": entity.validation_points
        }
    
    def _serialize_execution_flow(self, flow: ExecutionFlow) -> Dict[str, Any]:
        """Serialize an ExecutionFlow to JSON-compatible dict."""
        return {
            "name": flow.name,
            "entry_point": flow.entry_point,
            "steps": flow.steps,
            "files_involved": [str(f) for f in flow.files_involved],
            "description": flow.description
        }