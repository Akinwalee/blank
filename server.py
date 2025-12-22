from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import defaultdict
from typing import Dict
from urllib.parse import urlparse
from pathlib import PurePosixPath


get_routes = defaultdict(list)
post_routes = defaultdict(list)

def GET(path):
	def wrapper(func):
		get_routes[path] = func
		return func

	return wrapper

def POST(path):
	def wrapper(func):
		post_routes[path] = func
		return func

	return wrapper

class Router(BaseHTTPRequestHandler):
	def do_GET(self):
		url = urlparse(self.path)
		print(f"This is the URL {url}")
		query = transform_query(url.query)
		print(f"This is the transformed query: {query}")
		handler = get_routes.get(url.path)
		if handler:
			response = handler(**query)
			self.send_response(200)
		else:
			response = "404 Not Found"
			self.send_response(404)

		self.end_headers()
		self.wfile.write(response.encode())

	def do_POST(self):
		url = urlparse(self.path)
		print(f"This is the URL {url}")
		handler = post_routes.get(self.path)
		if handler:
			response = handler()
			self.send_response(200)
		else:
			response = "404 Not Found"
			self.send_response(404)

		self.end_headers()
		self.wfile.write(response.encode())


def transform_query(queries: str) -> Dict[str, str]:
	queries_list = queries.split('&')

	queries_map = {}

	for query in queries_list:
		query = query.split('=')
		queries_map[query[0]] = query[1]

	return queries_map

def get_params(path: str) -> dict:
	full_path = PurePosixPath(unquote(path))
	
