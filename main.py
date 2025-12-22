import routes
from server import HTTPServer, Router


server = HTTPServer(('localhost', 7740), Router)
print("Serving at http://localhost:7740")
server.serve_forever()