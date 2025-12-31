import re
from typing import Callable, Tuple, Dict, Any, TypeAlias


RouteHandler: TypeAlias = Callable[..., str]
RouteEntry: TypeAlias = Tuple[RouteHandler, re.Pattern]
RouteDict: TypeAlias = Dict[str, RouteEntry]
ParamsDict: TypeAlias = Dict[str, Any]