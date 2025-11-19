import http.server
import http.server

PORT = 8000

class Handler(http.server.CGIHTTPRequestHandler):
    def is_cgi(self):
        # Treat .py files as CGI scripts
        if '.py' in self.path:
            # Handle query parameters
            path_parts = self.path.split('?', 1)
            path = path_parts[0]
            if path.endswith('.py'):
                self.cgi_info = '', path[1:]
                return True
        return False

print(f"Serving on port {PORT}")
http.server.HTTPServer(("", PORT), Handler).serve_forever()
