from blank.common.parsing import URLParser


class TestNormalizePath:
    """Tests for path normalization."""
    
    def test_removes_trailing_slash(self):
        """Trailing slashes should be removed."""
        assert URLParser._normalize_path("/users/") == "/users"
        assert URLParser._normalize_path("/api/v1/") == "/api/v1"
    
    def test_preserves_root_path(self):
        """Root path '/' should not be modified."""
        assert URLParser._normalize_path("/") == "/"
    
    def test_preserves_path_without_trailing_slash(self):
        """Paths without trailing slash should not be modified."""
        assert URLParser._normalize_path("/users") == "/users"
        assert URLParser._normalize_path("/api/v1/users") == "/api/v1/users"
    
    def test_empty_path(self):
        """Empty path should remain empty."""
        assert URLParser._normalize_path("") == ""


class TestCoerceType:
    """Tests for type coercion."""
    
    def test_converts_integer(self):
        """String integers should become int."""
        assert URLParser._coerce_type("123") == 123
        assert URLParser._coerce_type("0") == 0
        assert URLParser._coerce_type("-42") == -42
        assert isinstance(URLParser._coerce_type("123"), int)
    
    def test_converts_float(self):
        """String floats should become float."""
        assert URLParser._coerce_type("3.14") == 3.14
        assert URLParser._coerce_type("-0.5") == -0.5
        assert URLParser._coerce_type("0.0") == 0.0
        assert isinstance(URLParser._coerce_type("3.14"), float)
    
    def test_converts_boolean_true(self):
        """'true' (case-insensitive) should become True."""
        assert URLParser._coerce_type("true") is True
        assert URLParser._coerce_type("True") is True
        assert URLParser._coerce_type("TRUE") is True
        assert URLParser._coerce_type("tRuE") is True
    
    def test_converts_boolean_false(self):
        """'false' (case-insensitive) should become False."""
        assert URLParser._coerce_type("false") is False
        assert URLParser._coerce_type("False") is False
        assert URLParser._coerce_type("FALSE") is False
        assert URLParser._coerce_type("fAlSe") is False
    
    def test_keeps_string(self):
        """Non-numeric, non-boolean strings should stay as strings."""
        assert URLParser._coerce_type("hello") == "hello"
        assert URLParser._coerce_type("John Doe") == "John Doe"
        assert URLParser._coerce_type("") == ""
        assert isinstance(URLParser._coerce_type("hello"), str)
    
    def test_string_not_confused_with_bool(self):
        """Strings like 'truthy' should not become booleans."""
        assert URLParser._coerce_type("truthy") == "truthy"
        assert URLParser._coerce_type("falsey") == "falsey"
        assert URLParser._coerce_type("yes") == "yes"
        assert URLParser._coerce_type("no") == "no"


class TestParseQuery:
    """Tests for query string parsing."""
    
    def test_parses_single_values(self):
        """Single values should be scalars, not lists."""
        result = URLParser._parse_query("name=John&age=30")
        assert result == {"name": "John", "age": 30}
    
    def test_parses_duplicate_keys_as_list(self):
        """Duplicate keys should become lists."""
        result = URLParser._parse_query("tag=python&tag=web&tag=api")
        assert result == {"tag": ["python", "web", "api"]}
    
    def test_mixed_single_and_duplicate(self):
        """Mix of single values and duplicates."""
        result = URLParser._parse_query("name=John&tag=a&tag=b")
        assert result == {"name": "John", "tag": ["a", "b"]}
    
    def test_empty_query_string(self):
        """Empty query string should return empty dict."""
        assert URLParser._parse_query("") == {}
    
    def test_blank_values(self):
        """Blank values should be preserved."""
        result = URLParser._parse_query("name=&flag=")
        assert result == {"name": "", "flag": ""}
    
    def test_type_coercion_in_query(self):
        """Query values should be type-coerced."""
        result = URLParser._parse_query("active=true&count=5&ratio=0.5")
        assert result == {"active": True, "count": 5, "ratio": 0.5}
    
    def test_url_encoded_values(self):
        """URL-encoded values should be decoded."""
        result = URLParser._parse_query("name=John%20Doe&path=%2Fapi%2Fv1")
        assert result == {"name": "John Doe", "path": "/api/v1"}


class TestPathToRegex:
    """Tests for path pattern to regex conversion."""
    
    def test_simple_path_no_params(self):
        """Path without params should match exactly."""
        pattern = URLParser.path_to_regex("/users")
        assert pattern.match("/users")
        assert not pattern.match("/users/123")
        assert not pattern.match("/user")
    
    def test_single_path_param(self):
        """Single path parameter should be captured."""
        pattern = URLParser.path_to_regex("/users/{id}")
        
        match = pattern.match("/users/123")
        assert match
        assert match.group("id") == "123"
        
        assert not pattern.match("/users")
        assert not pattern.match("/users/")
    
    def test_multiple_path_params(self):
        """Multiple path parameters should all be captured."""
        pattern = URLParser.path_to_regex("/users/{userId}/posts/{postId}")
        
        match = pattern.match("/users/42/posts/7")
        assert match
        assert match.group("userId") == "42"
        assert match.group("postId") == "7"
    
    def test_normalizes_trailing_slash_in_pattern(self):
        """Pattern with trailing slash should still match."""
        pattern = URLParser.path_to_regex("/users/{id}/")
        
        match = pattern.match("/users/123")
        assert match
        assert match.group("id") == "123"
    
    def test_special_regex_chars_escaped(self):
        """Special regex characters in path should be escaped."""
        pattern = URLParser.path_to_regex("/api.v1/users")
        assert pattern.match("/api.v1/users")
        assert not pattern.match("/apixv1/users")


class TestExtractPathParams:
    """Tests for path parameter extraction."""
    
    def test_extracts_single_param(self):
        """Should extract single path parameter."""
        pattern = URLParser.path_to_regex("/users/{id}")
        params = URLParser.extract_path_params(pattern, "/users/123")
        assert params == {"id": 123}
    
    def test_extracts_multiple_params(self):
        """Should extract multiple path parameters."""
        pattern = URLParser.path_to_regex("/users/{userId}/posts/{postId}")
        params = URLParser.extract_path_params(pattern, "/users/42/posts/7")
        assert params == {"userId": 42, "postId": 7}
    
    def test_coerces_param_types(self):
        """Path parameters should be type-coerced."""
        pattern = URLParser.path_to_regex("/items/{id}")
        
        assert URLParser.extract_path_params(pattern, "/items/123") == {"id": 123}
        assert URLParser.extract_path_params(pattern, "/items/hello") == {"id": "hello"}
    
    def test_returns_none_for_no_match(self):
        """Should return None if path doesn't match pattern."""
        pattern = URLParser.path_to_regex("/users/{id}")
        assert URLParser.extract_path_params(pattern, "/posts/123") is None
    
    def test_normalizes_path_before_matching(self):
        """Should normalize path before matching."""
        pattern = URLParser.path_to_regex("/users/{id}")
        params = URLParser.extract_path_params(pattern, "/users/123/")
        assert params == {"id": 123}
    
    def test_url_encoded_params(self):
        """URL-encoded path parameters should be decoded."""
        pattern = URLParser.path_to_regex("/users/{name}")
        params = URLParser.extract_path_params(pattern, "/users/John%20Doe")
        assert params == {"name": "John Doe"}


class TestURLParserInstance:
    """Tests for URLParser instance properties."""
    
    def test_path_property(self):
        """path property should return normalized path."""
        url = URLParser("/users/123?active=true")
        assert url.path == "/users/123"
    
    def test_path_with_trailing_slash(self):
        """path should normalize trailing slash."""
        url = URLParser("/users/")
        assert url.path == "/users"
    
    def test_query_property(self):
        """query property should return raw query string."""
        url = URLParser("/users?name=John&age=30")
        assert url.query == "name=John&age=30"
    
    def test_query_params_property(self):
        """query_params should return parsed and coerced dict."""
        url = URLParser("/users?active=true&count=5")
        assert url.query_params == {"active": True, "count": 5}
    
    def test_query_params_lazy_loaded(self):
        """query_params should be lazy-loaded."""
        url = URLParser("/users?name=John")
        assert url._query_params is None
        _ = url.query_params
        assert url._query_params is not None
    
    def test_no_query_string(self):
        """Should handle URLs without query string."""
        url = URLParser("/users/123")
        assert url.query == ""
        assert url.query_params == {}
