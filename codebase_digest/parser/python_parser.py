"""Python AST-based parser."""

import ast
from pathlib import Path
from typing import List, Optional

from .base import BaseParser
from ..models import Symbol, Import, CallRelation, DomainEntity


class PythonParser(BaseParser):
    """Parser for Python files using AST."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.py']
    
    def parse_symbols(self) -> List[Symbol]:
        """Extract Python symbols using AST."""
        symbols = []
        try:
            tree = ast.parse(self.content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbols.append(self._create_function_symbol(node))
                elif isinstance(node, ast.ClassDef):
                    symbols.append(self._create_class_symbol(node))
                    # Add methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            symbols.append(self._create_method_symbol(item, node.name))
                            
        except SyntaxError:
            # Skip files with syntax errors
            pass
            
        return symbols
    
    def parse_imports(self) -> List[Import]:
        """Extract import statements."""
        imports = []
        try:
            tree = ast.parse(self.content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(Import(
                            module=alias.name,
                            names=[alias.name],
                            alias=alias.asname,
                            file_path=self.file_path,
                            line_number=node.lineno
                        ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        names = [alias.name for alias in node.names]
                        imports.append(Import(
                            module=node.module,
                            names=names,
                            file_path=self.file_path,
                            line_number=node.lineno
                        ))
                        
        except SyntaxError:
            pass
            
        return imports
    
    def parse_calls(self) -> List[CallRelation]:
        """Extract function calls with symbol context."""
        calls = []
        try:
            tree = ast.parse(self.content)
            
            # First pass: collect all symbols for context
            symbols_by_name = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbol = self._create_function_symbol(node)
                    symbols_by_name[node.name] = symbol
                elif isinstance(node, ast.ClassDef):
                    class_symbol = self._create_class_symbol(node)
                    symbols_by_name[node.name] = class_symbol
                    # Add methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_symbol = self._create_method_symbol(item, node.name)
                            symbols_by_name[f"{node.name}.{item.name}"] = method_symbol
            
            # Second pass: extract calls with symbol context
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    caller_symbol = symbols_by_name.get(node.name)
                    if caller_symbol:
                        # Find calls within this function
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                callee_name = self._extract_call_name(child)
                                if callee_name:
                                    calls.append(CallRelation(
                                        caller_symbol=caller_symbol,
                                        callee_name=callee_name,
                                        line_number=child.lineno
                                    ))
                
                elif isinstance(node, ast.ClassDef):
                    # Handle method calls
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_key = f"{node.name}.{item.name}"
                            caller_symbol = symbols_by_name.get(method_key)
                            if caller_symbol:
                                # Find calls within this method
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        callee_name = self._extract_call_name(child)
                                        if callee_name:
                                            calls.append(CallRelation(
                                                caller_symbol=caller_symbol,
                                                callee_name=callee_name,
                                                line_number=child.lineno
                                            ))
                            
        except SyntaxError:
            pass
            
        return calls
    
    def _extract_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract the called function/method name from a Call node."""
        if isinstance(call_node.func, ast.Name):
            call_name = call_node.func.id
            # Filter out builtin functions
            if call_name in {'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum', 'min', 'max', 'abs', 'round', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'delattr'}:
                return None
            return call_name
        elif isinstance(call_node.func, ast.Attribute):
            attr_name = self._get_attribute_name_from_node(call_node.func)
            # Filter out common builtin method patterns
            if attr_name and any(pattern in attr_name.lower() for pattern in ['append', 'extend', 'pop', 'remove', 'insert', 'sort', 'reverse', 'datetime.now', 'time.time']):
                return None
            return attr_name
        return None
    
    def parse_domain_entities(self) -> List[DomainEntity]:
        """Extract domain entities (classes that represent business objects)."""
        entities = []
        try:
            tree = ast.parse(self.content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for common domain entity patterns
                    if self._is_domain_entity(node):
                        entity = DomainEntity(
                            name=node.name,
                            type='class',
                            file_path=self.file_path,
                            fields=self._extract_class_fields(node),
                            methods=self._extract_class_methods(node)
                        )
                        entities.append(entity)
                        
        except SyntaxError:
            pass
            
        return entities
    
    def _create_function_symbol(self, node: ast.FunctionDef) -> Symbol:
        """Create a Symbol from a function AST node."""
        return Symbol(
            name=node.name,
            type='function',
            file_path=self.file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            parameters=[arg.arg for arg in node.args.args],
            decorators=[self._get_decorator_name(dec) for dec in node.decorator_list]
        )
    
    def _create_class_symbol(self, node: ast.ClassDef) -> Symbol:
        """Create a Symbol from a class AST node."""
        return Symbol(
            name=node.name,
            type='class',
            file_path=self.file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            decorators=[self._get_decorator_name(dec) for dec in node.decorator_list]
        )
    
    def _create_method_symbol(self, node: ast.FunctionDef, class_name: str) -> Symbol:
        """Create a Symbol from a method AST node."""
        return Symbol(
            name=f"{class_name}.{node.name}",
            type='method',
            file_path=self.file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            parameters=[arg.arg for arg in node.args.args],
            decorators=[self._get_decorator_name(dec) for dec in node.decorator_list]
        )
    
    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return self._get_attribute_name_from_node(decorator) or ""
        return ""
    
    def _get_attribute_name_from_node(self, node: ast.Attribute) -> Optional[str]:
        """Get full attribute name (e.g., 'obj.method') from AST node."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            base = self._get_attribute_name_from_node(node.value)
            return f"{base}.{node.attr}" if base else None
        return None
    
    def _is_domain_entity(self, node: ast.ClassDef) -> bool:
        """Determine if a class represents a domain entity."""
        # Simple heuristics for domain entities
        class_name = node.name.lower()
        
        # Common domain entity names
        domain_keywords = [
            'user', 'account', 'profile', 'customer', 'client',
            'order', 'payment', 'transaction', 'invoice', 'billing',
            'product', 'item', 'catalog', 'inventory',
            'wallet', 'balance', 'credit', 'debit',
            'session', 'token', 'auth', 'permission',
            'notification', 'message', 'email', 'sms',
            'address', 'location', 'contact', 'phone'
        ]
        
        # Check if class name contains domain keywords
        for keyword in domain_keywords:
            if keyword in class_name:
                return True
        
        # Check for dataclass or pydantic model decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in ['dataclass', 'BaseModel']:
                    return True
        
        return False
    
    def _extract_class_fields(self, node: ast.ClassDef) -> List[str]:
        """Extract field names from a class."""
        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                fields.append(item.target.id)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        fields.append(target.id)
        return fields
    
    def _extract_class_methods(self, node: ast.ClassDef) -> List[str]:
        """Extract method names from a class."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        return methods