from blank import GET, POST


class TestGETRequests:
    """Tests for GET request handling."""
    
    def test_simple_get(self, client):
        """Simple GET request should return 200."""
        @GET("/hello")
        def hello():
            return "Hello, World!"
        
        response = client.get("/hello")
        assert response.status_code == 200
        assert response.text == "Hello, World!"
    
    def test_get_with_path_param(self, client):
        """GET with path parameter should extract and pass it."""
        @GET("/users/{id}")
        def get_user(id):
            return f"User {id}"
        
        response = client.get("/users/42")
        assert response.status_code == 200
        assert response.text == "User 42"
    
    def test_get_with_query_params(self, client):
        """GET with query parameters should parse and pass them."""
        @GET("/search")
        def search(q, limit=10):
            return f"Search: {q}, Limit: {limit}"
        
        response = client.get("/search?q=hello&limit=5")
        assert response.status_code == 200
        assert response.text == "Search: hello, Limit: 5"
    
    def test_get_with_path_and_query_params(self, client):
        """GET with both path and query parameters."""
        @GET("/users/{id}")
        def get_user(id, active=None):
            return f"User {id}, Active: {active}"
        
        response = client.get("/users/42?active=true")
        assert response.status_code == 200
        assert response.text == "User 42, Active: True"
    
    def test_get_multiple_path_params(self, client):
        """GET with multiple path parameters."""
        @GET("/users/{userId}/posts/{postId}")
        def get_post(userId, postId):
            return f"User {userId}, Post {postId}"
        
        response = client.get("/users/5/posts/123")
        assert response.status_code == 200
        assert response.text == "User 5, Post 123"
    
    def test_get_404(self, client):
        """GET to unknown route should return 404."""
        response = client.get("/unknown")
        assert response.status_code == 404
        assert response.text == "404 Not Found"
    
    def test_get_trailing_slash_normalized(self, client):
        """GET with trailing slash should match route."""
        @GET("/users/{id}")
        def get_user(id):
            return f"User {id}"
        
        response = client.get("/users/42/")
        assert response.status_code == 200
        assert response.text == "User 42"


class TestPOSTRequests:
    """Tests for POST request handling."""
    
    def test_simple_post(self, client):
        """Simple POST request should return 200."""
        @POST("/users")
        def create_user():
            return "User created"
        
        response = client.post("/users")
        assert response.status_code == 200
        assert response.text == "User created"
    
    def test_post_with_path_param(self, client):
        """POST with path parameter should extract and pass it."""
        @POST("/users/{id}/activate")
        def activate_user(id):
            return f"User {id} activated"
        
        response = client.post("/users/42/activate")
        assert response.status_code == 200
        assert response.text == "User 42 activated"
    
    def test_post_404(self, client):
        """POST to unknown route should return 404."""
        response = client.post("/unknown")
        assert response.status_code == 404


class TestTypeCoercion:
    """Tests for parameter type coercion in requests."""
    
    def test_integer_path_param(self, client):
        """Integer path parameters should be coerced."""
        @GET("/items/{id}")
        def get_item(id):
            return f"Type: {type(id).__name__}, Value: {id}"
        
        response = client.get("/items/123")
        assert "Type: int" in response.text
        assert "Value: 123" in response.text
    
    def test_boolean_query_param(self, client):
        """Boolean query parameters should be coerced."""
        @GET("/filter")
        def filter_items(active):
            return f"Type: {type(active).__name__}, Value: {active}"
        
        response = client.get("/filter?active=true")
        assert "Type: bool" in response.text
        assert "Value: True" in response.text
    
    def test_float_query_param(self, client):
        """Float query parameters should be coerced."""
        @GET("/calculate")
        def calculate(ratio):
            return f"Type: {type(ratio).__name__}, Value: {ratio}"
        
        response = client.get("/calculate?ratio=3.14")
        assert "Type: float" in response.text
        assert "Value: 3.14" in response.text
    
    def test_duplicate_query_params_as_list(self, client):
        """Duplicate query parameters should become a list."""
        @GET("/tags")
        def get_tags(tag):
            return f"Type: {type(tag).__name__}, Value: {tag}"
        
        response = client.get("/tags?tag=a&tag=b&tag=c")
        assert "Type: list" in response.text
        assert "['a', 'b', 'c']" in response.text


class TestResponseObject:
    """Tests for TestResponse object."""
    
    def test_ok_property_true(self, client):
        """ok should be True for 2xx status."""
        @GET("/test")
        def test_handler():
            return "ok"
        
        response = client.get("/test")
        assert response.ok is True
    
    def test_ok_property_false(self, client):
        """ok should be False for non-2xx status."""
        response = client.get("/nonexistent")
        assert response.ok is False
    
    def test_json_method(self, client):
        """json() should parse JSON response."""
        @GET("/data")
        def get_data():
            return '{"name": "John", "age": 30}'
        
        response = client.get("/data")
        data = response.json()
        assert data == {"name": "John", "age": 30}


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_missing_required_param(self, client):
        """Missing required parameter should return 500."""
        @GET("/greet")
        def greet(name):
            return f"Hello, {name}"
        
        response = client.get("/greet")
        assert response.status_code == 500
        assert "Internal Server Error" in response.text
    
    def test_method_not_allowed(self, client):
        """Using wrong HTTP method should return appropriate error."""
        @GET("/only-get")
        def only_get():
            return "GET only"
        
        response = client.post("/only-get")
        assert response.status_code == 404


class TestPathParamPrecedence:
    """Tests for parameter precedence."""
    
    def test_path_params_override_query_params(self, client):
        """Path parameters should take precedence over query parameters."""
        @GET("/users/{id}")
        def get_user(id):
            return f"id={id}"
        
        response = client.get("/users/42?id=999")
        assert response.text == "id=42"
