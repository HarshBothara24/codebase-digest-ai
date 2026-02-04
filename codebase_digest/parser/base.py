"""Base parser interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ..models import Symbol, Import, CallRelation, DomainEntity


class BaseParser(ABC):
    """Abstract base class for language-specific parsers."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = file_path.read_text(encoding='utf-8')
    
    @abstractmethod
    def parse_symbols(self) -> List[Symbol]:
        """Extract symbols (functions, classes, methods) from the file."""
        pass
    
    @abstractmethod
    def parse_imports(self) -> List[Import]:
        """Extract import statements from the file."""
        pass
    
    @abstractmethod
    def parse_calls(self) -> List[CallRelation]:
        """Extract function/method calls from the file."""
        pass
    
    @abstractmethod
    def parse_domain_entities(self) -> List[DomainEntity]:
        """Extract domain entities (business objects) from the file."""
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of file extensions this parser supports."""
        pass