from blank import GET, POST


@GET("/{path}")
def home(path, draft=None, skip=None):
    """Home route with path parameter and optional query params."""
    print(f"Query parameters: draft={draft}, skip={skip}")
    return f"Welcome to path: {path}!"

@GET("/users/{id}")
def get_user(id):
    """Get a user by ID."""
    return f"User {id}"

@GET("/users/{userId}/posts/{postId}")
def get_user_post(userId, postId):
    """Get a specific post from a user."""
    return f"User {userId}, Post {postId}"

@POST("/hello")
def hello():
    """Simple POST endpoint."""
    return "Saying hello and plenty greetings to you..."