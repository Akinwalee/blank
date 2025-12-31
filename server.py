from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Tuple, Callable, Optional, Any, Union
from urllib.parse import urlparse, parse_qs, unquote
import re


get_routes: Dict[str, Tuple[Callable, re.Pattern]] = {}
post_routes: Dict[str, Tuple[Callable, re.Pattern]] = {}


def normalize_path(path: str) -> str:
	"""Normalize path by removing trailing slash (except for root)."""
	if path != "/" and path.endswith("/"):
		return path.rstrip("/")
	return path


def coerce_type(value: str) -> Union[int, float, bool, str]:
	"""Auto-convert string to appropriate Python type."""
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


def path_to_regex(path: str) -> re.Pattern:
	"""Convert a path pattern like /users/{id} to a compiled regex with named groups."""
	regex_path = re.escape(path)
	regex_path = re.sub(r'\\{(\w+)\\}', r'(?P<\1>[^/]+)', regex_path)
	return re.compile(f'^{regex_path}$')


def GET(path: str):
	"""Decorator to register a GET route handler."""
	def wrapper(func: Callable):
		normalized_path = normalize_path(path)
		get_routes[normalized_path] = (func, path_to_regex(normalized_path))
		return func
	return wrapper


def POST(path: str):
	"""Decorator to register a POST route handler."""
	def wrapper(func: Callable):
		normalized_path = normalize_path(path)
		post_routes[normalized_path] = (func, path_to_regex(normalized_path))
		return func
	return wrapper


def find_route(
	routes: Dict[str, Tuple[Callable, re.Pattern]],
	path: str
) -> Tuple[Optional[Callable], Dict[str, Any]]:
	"""Find a matching route and extract path parameters."""
	normalized_path = normalize_path(path)
	
	for handler, pattern in routes.values():
		match = pattern.match(normalized_path)
		if match:
			path_params = {
				name: coerce_type(unquote(value))
				for name, value in match.groupdict().items()
			}
			return handler, path_params
	
	return None, {}


def transform_query(query_string: str) -> Dict[str, Any]:
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
		coerced_values = [coerce_type(unquote(v)) for v in values]
		
		if len(coerced_values) == 1:
			result[key] = coerced_values[0]
		else:
			result[key] = coerced_values
	
	return result


class Router(BaseHTTPRequestHandler):
	def do_GET(self):
		url = urlparse(self.path)
		
		query_params = transform_query(url.query)
		
		handler, path_params = find_route(get_routes, url.path)
		
		if handler:
			all_params = {**query_params, **path_params}
			response = handler(**all_params)
			self.send_response(200)
		else:
			response = "404 Not Found"
			self.send_response(404)

		self.end_headers()
		self.wfile.write(response.encode())

	def do_POST(self):
		url = urlparse(self.path)
		
		query_params = transform_query(url.query)
		
		handler, path_params = find_route(post_routes, url.path)
		
		if handler:
			all_params = {**query_params, **path_params}
			response = handler(**all_params)
			self.send_response(200)
		else:
			response = "404 Not Found"
			self.send_response(404)

		self.end_headers()
		self.wfile.write(response.encode())
	
