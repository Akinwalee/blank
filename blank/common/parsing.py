import re
from typing import Dict, Optional, Any, Union
from urllib.parse import urlparse, parse_qs, unquote


class URLParser:
    """Parses URLs and extracts path parameters, query parameters with type coercion.
    
    Example:
        url = URLParser('/users/123?draft=true&skip=5')
        print(url.path)          # '/users/123'
        print(url.query_params)  # {'draft': True, 'skip': 5}
    """
    
    def __init__(self, url: str):
        """Initialize parser with a URL string."""
        self._parsed = urlparse(url)
        self._path = self._normalize_path(self._parsed.path)
        self._query_params: Optional[Dict[str, Any]] = None
    
    @property
    def path(self) -> str:
        """Get the normalized path."""
        return self._path
    
    @property
    def query(self) -> str:
        """Get the raw query string."""
        return self._parsed.query
    
    @property
    def query_params(self) -> Dict[str, Any]:
        """Get parsed query parameters with type coercion (lazy-loaded)."""
        if self._query_params is None:
            self._query_params = self._parse_query(self._parsed.query)
        return self._query_params
    
    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path by removing trailing slash (except for root)."""
        if path != "/" and path.endswith("/"):
            return path.rstrip("/")
        return path
    
    @staticmethod
    def _coerce_type(value: str) -> Union[int, float, bool, str]:
        """Convert string to appropriate Python type."""
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        
        try:
            return int(value)
        except ValueError:
            pass
        
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    @classmethod
    def _parse_query(cls, query_string: str) -> Dict[str, Any]:
        """Parse query string into a dictionary with type coercion.
        
        - Single values are returned as scalars
        - Duplicate keys are returned as lists
        - Values are auto-converted to int, float, bool, or str
        """
        if not query_string:
            return {}
        
        parsed = parse_qs(query_string, keep_blank_values=True)
        
        result = {}
        for key, values in parsed.items():
            coerced_values = [cls._coerce_type(unquote(v)) for v in values]
            
            if len(coerced_values) == 1:
                result[key] = coerced_values[0]
            else:
                result[key] = coerced_values
        
        return result
    
    @classmethod
    def path_to_regex(cls, path: str) -> re.Pattern:
        """Convert a path pattern like /users/{id} to a compiled regex with named groups.
        
        Args:
            path: URL path pattern with {param} placeholders
            
        Returns:
            Compiled regex pattern with named capture groups
            
        Example:
            pattern = URLParser.path_to_regex('/users/{id}')
            # pattern.pattern == '^/users/(?P<id>[^/]+)$'
        """
        normalized = cls._normalize_path(path)
        regex_path = re.escape(normalized)
        regex_path = re.sub(r'\\{(\w+)\\}', r'(?P<\1>[^/]+)', regex_path)
        return re.compile(f'^{regex_path}$')
    
    @classmethod
    def extract_path_params(cls, pattern: re.Pattern, path: str) -> Optional[Dict[str, Any]]:
        """Extract path parameters from a URL path using a compiled regex pattern.
        
        Args:
            pattern: Compiled regex pattern from path_to_regex
            path: URL path to extract parameters from
            
        Returns:
            Dictionary of extracted parameters with type coercion,
            or None if path doesn't match pattern
        """
        normalized = cls._normalize_path(path)
        match = pattern.match(normalized)
        
        if not match:
            return None
        
        return {
            name: cls._coerce_type(unquote(value))
            for name, value in match.groupdict().items()
        }
