"""JavaScript/TypeScript parser using tree-sitter."""

from pathlib import Path
from typing import List

from .base import BaseParser
from ..models import Symbol, Import, CallRelation, DomainEntity


class JavaScriptParser(BaseParser):
    """Parser for JavaScript/TypeScript files using tree-sitter."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.js', '.jsx', '.ts', '.tsx']
    
    def parse_symbols(self) -> List[Symbol]:
        """Extract JavaScript/TypeScript symbols."""
        # TODO: Implement tree-sitter parsing
        # For now, return empty list as placeholder
        return []
    
    def parse_imports(self) -> List[Import]:
        """Extract import statements."""
        # TODO: Implement tree-sitter parsing
        return []
    
    def parse_calls(self) -> List[CallRelation]:
        """Extract function calls."""
        # TODO: Implement tree-sitter parsing
        return []
    
    def parse_domain_entities(self) -> List[DomainEntity]:
        """Extract domain entities."""
        # TODO: Implement tree-sitter parsing
        return []