"""Core data models for codebase analysis."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from pathlib import Path


@dataclass
class Symbol:
    """Represents a code symbol (function, class, method, etc.)."""
    name: str
    type: str  # 'function', 'class', 'method', 'variable'
    file_path: Path
    line_number: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)


@dataclass
class Import:
    """Represents an import statement."""
    module: str
    names: List[str]
    alias: Optional[str] = None
    file_path: Optional[Path] = None
    line_number: Optional[int] = None


@dataclass
class CallRelation:
    """Represents a function/method call relationship."""
    caller_symbol: Symbol
    callee_name: str
    line_number: Optional[int] = None
    callee_file: Optional[Path] = None  # For cross-file calls


@dataclass
class DomainEntity:
    """Represents a domain entity (business object)."""
    name: str
    type: str  # 'class', 'dataclass', 'pydantic_model', etc.
    file_path: Path
    fields: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    creation_points: List[str] = field(default_factory=list)
    modification_points: List[str] = field(default_factory=list)
    validation_points: List[str] = field(default_factory=list)


@dataclass
class ExecutionFlow:
    """Represents an execution flow through the system."""
    name: str
    entry_point: str
    steps: List[str] = field(default_factory=list)
    files_involved: Set[Path] = field(default_factory=set)
    description: Optional[str] = None


@dataclass
class CodebaseAnalysis:
    """Complete analysis results for a codebase."""
    root_path: Path
    symbols: List[Symbol] = field(default_factory=list)
    imports: List[Import] = field(default_factory=list)
    call_relations: List[CallRelation] = field(default_factory=list)
    domain_entities: List[DomainEntity] = field(default_factory=list)
    execution_flows: List[ExecutionFlow] = field(default_factory=list)
    entry_points: List[Path] = field(default_factory=list)
    
    # Metrics
    total_files: int = 0
    total_lines: int = 0
    languages: Set[str] = field(default_factory=set)
    complexity_score: float = 0.0
    
    # Directory structure
    directory_tree: Dict = field(default_factory=dict)