from dataclasses import dataclass
from typing import Optional, Dict, Any

from blank.common.parsing import URLParser
from blank.core.routing import get_routes, post_routes, find_route


@dataclass
class TestResponse:
    """Response object returned by TestClient.
    
    Attributes:
        status_code: HTTP status code (200, 404, etc.)
        text: Response body as string
        headers: Response headers dict
    """
    status_code: int
    text: str
    headers: Dict[str, str]
    
    @property
    def ok(self) -> bool:
        """True if status_code is 2xx."""
        return 200 <= self.status_code < 300
    
    def json(self) -> Any:
        """Parse response body as JSON."""
        import json
        return json.loads(self.text)


class Client:
    """HTTP client for testing routes without a real server.
    
    Calls route handlers directly, simulating HTTP request/response flow.
    
    Example:
        client = Client()
        response = client.get('/users/42?active=true')
        assert response.status_code == 200
    """
    
    def __init__(self):
        """Initialize the test client."""
        pass
    
    def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        """Make a GET request.
        
        Args:
            path: URL path with optional query string (e.g., '/users/42?active=true')
            headers: Optional request headers
            
        Returns:
            TestResponse with status_code, text, and headers
        """
        return self._request("GET", path, headers)
    
    def post(self, path: str, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        """Make a POST request.
        
        Args:
            path: URL path with optional query string
            headers: Optional request headers
            
        Returns:
            TestResponse with status_code, text, and headers
        """
        return self._request("POST", path, headers)
    
    def _request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None
    ) -> TestResponse:
        """Internal method to process a request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: URL path with optional query string
            headers: Optional request headers
            
        Returns:
            TestResponse with status_code, text, and headers
        """
        if method == "GET":
            routes = get_routes
        elif method == "POST":
            routes = post_routes
        else:
            return TestResponse(
                status_code=405,
                text="Method Not Allowed",
                headers={"Content-Type": "text/plain"}
            )
        
        url = URLParser(path)
        handler, path_params = find_route(routes, url.path)
        
        if handler:
            all_params = {**url.query_params, **path_params}
            
            try:
                response_text = handler(**all_params)
                return TestResponse(
                    status_code=200,
                    text=str(response_text),
                    headers={"Content-Type": "text/plain"}
                )
            except TypeError as e:
                return TestResponse(
                    status_code=500,
                    text=f"Internal Server Error: {e}",
                    headers={"Content-Type": "text/plain"}
                )
            except Exception as e:
                return TestResponse(
                    status_code=500,
                    text=f"Internal Server Error: {e}",
                    headers={"Content-Type": "text/plain"}
                )
        else:
            return TestResponse(
                status_code=404,
                text="404 Not Found",
                headers={"Content-Type": "text/plain"}
            )
