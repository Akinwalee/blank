from server import GET, POST


@GET("/{path}")
def home(draft, skip, path):
	print(f"These are the query parameters: draft --> {draft}, skip --> {skip}")
	# print(f"And this the great path parameter: {path}")
	return "Welcome home, blank!"

@POST("/hello")
def hello():
	return "Saying hello and plenty greetings to you..."


