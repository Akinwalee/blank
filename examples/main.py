import examples.app  # noqa: F401

from blank import HTTPServer, Router


def main():
    host = "localhost"
    port = 7740
    
    server = HTTPServer((host, port), Router)
    print(f"Server running at http://{host}:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()