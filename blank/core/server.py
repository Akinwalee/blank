from http.server import BaseHTTPRequestHandler, HTTPServer

from blank.common.parsing import URLParser
from blank.core.routing import get_routes, post_routes, find_route


__all__ = ["Router", "HTTPServer"]


class Router(BaseHTTPRequestHandler):
    """HTTP request handler with routing support."""
    
    def do_GET(self):
        """Handle GET requests."""
        url = URLParser(self.path)
        handler, path_params = find_route(get_routes, url.path)
        
        if handler:
            all_params = {**url.query_params, **path_params}
            response = handler(**all_params)
            self.send_response(200)
        else:
            response = "404 Not Found"
            self.send_response(404)

        self.end_headers()
        self.wfile.write(response.encode())

    def do_POST(self):
        """Handle POST requests."""
        url = URLParser(self.path)
        handler, path_params = find_route(post_routes, url.path)
        
        if handler:
            all_params = {**url.query_params, **path_params}
            response = handler(**all_params)
            self.send_response(200)
        else:
            response = "404 Not Found"
            self.send_response(404)

        self.end_headers()
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[{self.log_date_time_string()}] {format % args}")
