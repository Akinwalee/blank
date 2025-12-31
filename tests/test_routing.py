from blank import GET, POST
from blank.core.routing import get_routes, post_routes, find_route


class TestGETDecorator:
    """Tests for @GET decorator."""
    
    def test_registers_route(self):
        """@GET should register route in get_routes."""
        @GET("/users")
        def get_users():
            return "users"
        
        assert "/users" in get_routes
    
    def test_stores_handler_function(self):
        """Route entry should contain the handler function."""
        @GET("/test")
        def test_handler():
            return "test"
        
        handler, _ = get_routes["/test"]
        assert handler is test_handler
    
    def test_stores_compiled_pattern(self):
        """Route entry should contain compiled regex pattern."""
        @GET("/users/{id}")
        def get_user(id):
            return f"user {id}"
        
        _, pattern = get_routes["/users/{id}"]
        assert pattern.match("/users/123")
    
    def test_returns_original_function(self):
        """Decorator should return the original function."""
        @GET("/test")
        def my_handler():
            return "test"
        
        assert my_handler() == "test"
    
    def test_multiple_routes(self):
        """Multiple routes can be registered."""
        @GET("/route1")
        def handler1():
            return "1"
        
        @GET("/route2")
        def handler2():
            return "2"
        
        assert "/route1" in get_routes
        assert "/route2" in get_routes


class TestPOSTDecorator:
    """Tests for @POST decorator."""
    
    def test_registers_route(self):
        """@POST should register route in post_routes."""
        @POST("/users")
        def create_user():
            return "created"
        
        assert "/users" in post_routes
    
    def test_stores_handler_function(self):
        """Route entry should contain the handler function."""
        @POST("/test")
        def test_handler():
            return "test"
        
        handler, pattern = post_routes["/test"]
        assert handler is test_handler
    
    def test_separate_from_get_routes(self):
        """GET and POST routes should be stored separately."""
        @GET("/users")
        def get_users():
            return "get"
        
        @POST("/users")
        def create_user():
            return "post"
        
        assert "/users" in get_routes
        assert "/users" in post_routes
        
        get_handler, _ = get_routes["/users"]
        post_handler, _ = post_routes["/users"]
        
        assert get_handler() == "get"
        assert post_handler() == "post"


class TestFindRoute:
    """Tests for find_route function."""
    
    def test_finds_exact_match(self):
        """Should find route with exact path match."""
        @GET("/users")
        def get_users():
            return "users"
        
        handler, params = find_route(get_routes, "/users")
        assert handler is get_users
        assert params == {}
    
    def test_extracts_path_params(self):
        """Should extract path parameters."""
        @GET("/users/{id}")
        def get_user(id):
            return f"user {id}"
        
        handler, params = find_route(get_routes, "/users/123")
        assert handler is get_user
        assert params == {"id": 123}
    
    def test_extracts_multiple_path_params(self):
        """Should extract multiple path parameters."""
        @GET("/users/{userId}/posts/{postId}")
        def get_post(userId, postId):
            return f"user {userId} post {postId}"
        
        handler, params = find_route(get_routes, "/users/42/posts/7")
        assert params == {"userId": 42, "postId": 7}
    
    def test_returns_none_for_no_match(self):
        """Should return (None, {}) when no route matches."""
        @GET("/users")
        def get_users():
            return "users"
        
        handler, params = find_route(get_routes, "/posts")
        assert handler is None
        assert params == {}
    
    def test_normalizes_trailing_slash(self):
        """Should match paths with trailing slash."""
        @GET("/users/{id}")
        def get_user(id):
            return f"user {id}"
        
        handler, params = find_route(get_routes, "/users/123/")
        assert handler is get_user
        assert params == {"id": 123}
    
    def test_coerces_path_param_types(self):
        """Path parameters should be type-coerced."""
        @GET("/items/{id}")
        def get_item(id):
            return f"item {id}"
        
        handler, params = find_route(get_routes, "/items/42")
        assert params["id"] == 42
        assert isinstance(params["id"], int)
        
        handler, params = find_route(get_routes, "/items/hello")
        assert params["id"] == "hello"
        assert isinstance(params["id"], str)


class TestRouteIsolation:
    """Tests to verify route isolation between tests."""
    
    def test_routes_are_empty_at_start(self):
        """Routes should be empty at the start of each test."""
        assert len(get_routes) == 0
        assert len(post_routes) == 0
    
    def test_register_route_for_isolation_check(self):
        """Register a route to verify it doesn't leak."""
        @GET("/isolation-test")
        def isolation_handler():
            return "isolation"
        
        assert "/isolation-test" in get_routes
    
    def test_previous_route_not_present(self):
        """Route from previous test should not be present."""
        assert "/isolation-test" not in get_routes
