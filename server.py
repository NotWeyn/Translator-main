from http.server import SimpleHTTPRequestHandler, HTTPServer

class ForceDownloadHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Disposition", "attachment")
        super().end_headers()

PORT = 8000

with HTTPServer(("", PORT), ForceDownloadHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
