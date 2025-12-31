import re
from typing import Dict, Tuple, Callable, Optional, Any

from blank.common.parsing import URLParser
from blank.common.types import RouteDict

get_routes: RouteDict = {}
post_routes: RouteDict = {}


def GET(path: str):
    """Decorator to register a GET route handler.
    
    Example:
        @GET('/users/{id}')
        def get_user(id):
            return f'User {id}'
    """
    def wrapper(func: Callable):
        pattern = URLParser.path_to_regex(path)
        get_routes[path] = (func, pattern)
        return func
    return wrapper


def POST(path: str):
    """Decorator to register a POST route handler.
    
    Example:
        @POST('/users')
        def create_user():
            return 'User created'
    """
    def wrapper(func: Callable):
        pattern = URLParser.path_to_regex(path)
        post_routes[path] = (func, pattern)
        return func
    return wrapper


def find_route(
    routes: Dict[str, Tuple[Callable, re.Pattern]],
    path: str
) -> Tuple[Optional[Callable], Dict[str, Any]]:
    """Find a matching route and extract path parameters.
    
    Args:
        routes: Dictionary of registered routes
        path: URL path to match
        
    Returns:
        Tuple of (handler function, path parameters dict)
        Returns (None, {}) if no match found
    """
    for handler, pattern in routes.values():
        path_params = URLParser.extract_path_params(pattern, path)
        if path_params is not None:
            return handler, path_params
    
    return None, {}
